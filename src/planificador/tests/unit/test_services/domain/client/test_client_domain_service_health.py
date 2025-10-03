# -*- coding: utf-8 -*-
"""
Tests para Operaciones de Salud - ClientDomainService

Tests completos para verificar el correcto funcionamiento de las operaciones
de salud, diagnóstico y monitoreo del servicio de dominio cliente.
"""

import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from planificador.exceptions import BusinessLogicError, RepositoryError


class TestClientDomainServiceHealthOperations:
    """Tests para operaciones de salud del ClientDomainService."""

    @pytest.mark.asyncio
    async def test_check_service_health_success(self, client_domain_service):
        """Test verificación exitosa de salud del servicio."""
        # Arrange
        expected_result = {
            "service_name": "ClientDomainService",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "healthy",
            "version": "1.0.0",
            "components": {
                "database": {"status": "connected", "latency_ms": 15},
                "repository": {"status": "operational", "modules": 8}
            },
            "metrics": {
                "response_time_seconds": 0.125,
                "memory_usage_mb": 45.2,
                "active_connections": 3
            },
            "errors": []
        }
        
        client_domain_service.health.check_service_health.return_value = expected_result

        # Act
        result = await client_domain_service.check_service_health()

        # Assert
        assert result == expected_result
        assert result["status"] == "healthy"
        assert "components" in result
        assert "metrics" in result
        assert result["errors"] == []
        client_domain_service.health.check_service_health.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_service_health_degraded(self, client_domain_service):
        """Test verificación de salud con estado degradado."""
        # Arrange
        expected_result = {
            "service_name": "ClientDomainService",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "degraded",
            "version": "1.0.0",
            "components": {
                "database": {"status": "connected", "latency_ms": 150},
                "repository": {"status": "operational", "modules": 8}
            },
            "metrics": {
                "response_time_seconds": 2.5,
                "memory_usage_mb": 85.7,
                "active_connections": 12
            },
            "errors": ["High latency detected", "Memory usage above threshold"]
        }
        
        client_domain_service.health.check_service_health.return_value = expected_result

        # Act
        result = await client_domain_service.check_service_health()

        # Assert
        assert result == expected_result
        assert result["status"] == "degraded"
        assert len(result["errors"]) == 2
        assert "High latency detected" in result["errors"]
        client_domain_service.health.check_service_health.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_service_health_critical(self, client_domain_service):
        """Test verificación de salud con estado crítico."""
        # Arrange
        expected_result = {
            "service_name": "ClientDomainService",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "critical",
            "version": "1.0.0",
            "components": {
                "database": {"status": "disconnected", "latency_ms": None},
                "repository": {"status": "error", "modules": 0}
            },
            "metrics": {
                "response_time_seconds": None,
                "memory_usage_mb": 120.5,
                "active_connections": 0
            },
            "errors": ["Database connection failed", "Repository facade unavailable"]
        }
        
        client_domain_service.health.check_service_health.return_value = expected_result

        # Act
        result = await client_domain_service.check_service_health()

        # Assert
        assert result == expected_result
        assert result["status"] == "critical"
        assert len(result["errors"]) == 2
        assert "Database connection failed" in result["errors"]
        client_domain_service.health.check_service_health.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_service_health_error(self, client_domain_service):
        """Test error durante verificación de salud del servicio."""
        # Arrange
        client_domain_service.health.check_service_health.side_effect = BusinessLogicError(
            message="Error durante verificación de salud"
        )

        # Act & Assert
        with pytest.raises(BusinessLogicError) as exc_info:
            await client_domain_service.check_service_health()
        
        assert "Error durante verificación de salud" in str(exc_info.value)
        client_domain_service.health.check_service_health.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_database_connectivity_success(self, client_domain_service):
        """Test verificación exitosa de conectividad de base de datos."""
        # Arrange
        expected_result = {
            "status": "connected",
            "timestamp": "2024-01-01T00:00:00Z",
            "database_info": {
                "type": "sqlite",
                "version": "3.40.0",
                "file_path": "/path/to/database.db",
                "size_mb": 15.7
            },
            "connection_pool": {
                "active_connections": 3,
                "idle_connections": 2,
                "max_connections": 10
            },
            "tests": {
                "basic_query": {"status": "success", "duration_ms": 5},
                "write_test": {"status": "success", "duration_ms": 12},
                "latency": {"status": "good", "latency_ms": 8}
            },
            "performance_metrics": {
                "total_check_time_seconds": 0.045,
                "queries_executed": 3,
                "average_response_time_ms": 8.3
            }
        }
        
        client_domain_service.health.check_database_connectivity.return_value = expected_result

        # Act
        result = await client_domain_service.check_database_connectivity()

        # Assert
        assert result == expected_result
        assert result["status"] == "connected"
        assert "database_info" in result
        assert "connection_pool" in result
        assert "tests" in result
        assert result["tests"]["basic_query"]["status"] == "success"
        client_domain_service.health.check_database_connectivity.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_database_connectivity_disconnected(self, client_domain_service):
        """Test verificación de conectividad con base de datos desconectada."""
        # Arrange
        expected_result = {
            "status": "disconnected",
            "timestamp": "2024-01-01T00:00:00Z",
            "database_info": None,
            "connection_pool": {
                "active_connections": 0,
                "idle_connections": 0,
                "max_connections": 10
            },
            "tests": {
                "basic_query": {"status": "failed", "error": "Connection timeout"},
                "write_test": {"status": "failed", "error": "Connection timeout"},
                "latency": {"status": "failed", "error": "Connection timeout"}
            },
            "performance_metrics": {
                "total_check_time_seconds": 5.0,
                "queries_executed": 0,
                "average_response_time_ms": None
            },
            "errors": ["Database connection timeout", "Unable to execute test queries"]
        }
        
        client_domain_service.health.check_database_connectivity.return_value = expected_result

        # Act
        result = await client_domain_service.check_database_connectivity()

        # Assert
        assert result == expected_result
        assert result["status"] == "disconnected"
        assert len(result["errors"]) == 2
        assert "Database connection timeout" in result["errors"]
        client_domain_service.health.check_database_connectivity.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_database_connectivity_error(self, client_domain_service):
        """Test error durante verificación de conectividad de base de datos."""
        # Arrange
        client_domain_service.health.check_database_connectivity.side_effect = BusinessLogicError(
            message="Error durante verificación de conectividad"
        )

        # Act & Assert
        with pytest.raises(BusinessLogicError) as exc_info:
            await client_domain_service.check_database_connectivity()
        
        assert "Error durante verificación de conectividad" in str(exc_info.value)
        client_domain_service.health.check_database_connectivity.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_health_report_success(self, client_domain_service):
        """Test generación exitosa de reporte completo de salud."""
        # Arrange
        expected_result = {
            "report_metadata": {
                "generated_at": "2024-01-01T00:00:00Z",
                "report_version": "1.0.0",
                "service_name": "ClientDomainService",
                "report_type": "comprehensive_health_check"
            },
            "executive_summary": {
                "overall_status": "healthy",
                "critical_issues": [],
                "warnings": [],
                "recommendations": ["Consider implementing caching for improved performance"]
            },
            "detailed_analysis": {
                "service_health": {
                    "status": "healthy",
                    "components": {"database": "connected", "repository": "operational"}
                },
                "database_connectivity": {
                    "status": "connected",
                    "performance": "good"
                },
                "repository_modules": {
                    "total_modules": 8,
                    "operational_modules": 8,
                    "status": "all_operational"
                }
            },
            "performance_metrics": {
                "response_times": {
                    "service_health_check": 0.125,
                    "database_connectivity": 0.045
                },
                "resource_usage": {
                    "memory_usage_mb": 45.2,
                    "cpu_usage_percent": 12.5
                },
                "database_performance": {
                    "average_query_time_ms": 8.3,
                    "connection_pool_usage": 0.5
                }
            },
            "maintenance_recommendations": [
                "Schedule regular database maintenance",
                "Monitor memory usage trends",
                "Consider connection pool optimization"
            ]
        }
        
        client_domain_service.health.generate_health_report.return_value = expected_result

        # Act
        result = await client_domain_service.generate_health_report()

        # Assert
        assert result == expected_result
        assert result["executive_summary"]["overall_status"] == "healthy"
        assert "report_metadata" in result
        assert "detailed_analysis" in result
        assert "performance_metrics" in result
        assert len(result["maintenance_recommendations"]) == 3
        client_domain_service.health.generate_health_report.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_health_report_with_issues(self, client_domain_service):
        """Test generación de reporte de salud con problemas detectados."""
        # Arrange
        expected_result = {
            "report_metadata": {
                "generated_at": "2024-01-01T00:00:00Z",
                "report_version": "1.0.0",
                "service_name": "ClientDomainService",
                "report_type": "comprehensive_health_check"
            },
            "executive_summary": {
                "overall_status": "degraded",
                "critical_issues": ["High database latency detected"],
                "warnings": ["Memory usage approaching limits"],
                "recommendations": [
                    "Optimize database queries",
                    "Increase memory allocation",
                    "Review connection pool configuration"
                ]
            },
            "detailed_analysis": {
                "service_health": {
                    "status": "degraded",
                    "components": {"database": "slow", "repository": "operational"}
                },
                "database_connectivity": {
                    "status": "connected",
                    "performance": "degraded",
                    "latency_ms": 250
                },
                "repository_modules": {
                    "total_modules": 8,
                    "operational_modules": 7,
                    "status": "mostly_operational"
                }
            },
            "performance_metrics": {
                "response_times": {
                    "service_health_check": 2.5,
                    "database_connectivity": 0.8
                },
                "resource_usage": {
                    "memory_usage_mb": 85.7,
                    "cpu_usage_percent": 45.2
                },
                "database_performance": {
                    "average_query_time_ms": 125.6,
                    "connection_pool_usage": 0.9
                }
            },
            "maintenance_recommendations": [
                "URGENT: Optimize slow database queries",
                "Monitor memory usage closely",
                "Consider scaling database resources",
                "Review and optimize connection pooling"
            ]
        }
        
        client_domain_service.health.generate_health_report.return_value = expected_result

        # Act
        result = await client_domain_service.generate_health_report()

        # Assert
        assert result == expected_result
        assert result["executive_summary"]["overall_status"] == "degraded"
        assert len(result["executive_summary"]["critical_issues"]) == 1
        assert len(result["executive_summary"]["warnings"]) == 1
        assert len(result["executive_summary"]["recommendations"]) == 3
        assert "URGENT" in result["maintenance_recommendations"][0]
        client_domain_service.health.generate_health_report.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_health_report_critical_state(self, client_domain_service):
        """Test generación de reporte de salud en estado crítico."""
        # Arrange
        expected_result = {
            "report_metadata": {
                "generated_at": "2024-01-01T00:00:00Z",
                "report_version": "1.0.0",
                "service_name": "ClientDomainService",
                "report_type": "comprehensive_health_check"
            },
            "executive_summary": {
                "overall_status": "critical",
                "critical_issues": [
                    "Database connection failed",
                    "Multiple repository modules offline",
                    "Service response time exceeded threshold"
                ],
                "warnings": ["System requires immediate attention"],
                "recommendations": [
                    "IMMEDIATE: Restore database connectivity",
                    "IMMEDIATE: Restart repository services",
                    "IMMEDIATE: Check system resources"
                ]
            },
            "detailed_analysis": {
                "service_health": {
                    "status": "critical",
                    "components": {"database": "disconnected", "repository": "error"}
                },
                "database_connectivity": {
                    "status": "disconnected",
                    "performance": "unavailable"
                },
                "repository_modules": {
                    "total_modules": 8,
                    "operational_modules": 2,
                    "status": "critical_failure"
                }
            },
            "performance_metrics": {
                "response_times": {
                    "service_health_check": None,
                    "database_connectivity": None
                },
                "resource_usage": {
                    "memory_usage_mb": 120.5,
                    "cpu_usage_percent": 85.0
                },
                "database_performance": {
                    "average_query_time_ms": None,
                    "connection_pool_usage": 0.0
                }
            },
            "maintenance_recommendations": [
                "CRITICAL: Immediate system restart required",
                "CRITICAL: Database recovery procedures needed",
                "CRITICAL: Contact system administrator",
                "Review system logs for root cause analysis"
            ]
        }
        
        client_domain_service.health.generate_health_report.return_value = expected_result

        # Act
        result = await client_domain_service.generate_health_report()

        # Assert
        assert result == expected_result
        assert result["executive_summary"]["overall_status"] == "critical"
        assert len(result["executive_summary"]["critical_issues"]) == 3
        assert "IMMEDIATE" in result["executive_summary"]["recommendations"][0]
        assert "CRITICAL" in result["maintenance_recommendations"][0]
        client_domain_service.health.generate_health_report.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_health_report_error(self, client_domain_service):
        """Test error durante generación de reporte de salud."""
        # Arrange
        client_domain_service.health.generate_health_report.side_effect = BusinessLogicError(
            message="Error durante generación de reporte de salud"
        )

        # Act & Assert
        with pytest.raises(BusinessLogicError) as exc_info:
            await client_domain_service.generate_health_report()
        
        assert "Error durante generación de reporte de salud" in str(exc_info.value)
        client_domain_service.health.generate_health_report.assert_called_once()


class TestClientDomainServiceHealthIntegration:
    """Tests de integración para operaciones de salud."""

    @pytest.mark.asyncio
    async def test_health_operations_integration_flow(self, client_domain_service):
        """Test flujo completo de operaciones de salud."""
        # Arrange
        service_health = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "components": {"database": "connected", "repository": "operational"}
        }
        
        db_connectivity = {
            "status": "connected",
            "timestamp": "2024-01-01T00:00:00Z",
            "performance": "good"
        }
        
        health_report = {
            "executive_summary": {"overall_status": "healthy"},
            "detailed_analysis": {
                "service_health": service_health,
                "database_connectivity": db_connectivity
            }
        }
        
        client_domain_service.health.check_service_health.return_value = service_health
        client_domain_service.health.check_database_connectivity.return_value = db_connectivity
        client_domain_service.health.generate_health_report.return_value = health_report

        # Act
        service_result = await client_domain_service.check_service_health()
        db_result = await client_domain_service.check_database_connectivity()
        report_result = await client_domain_service.generate_health_report()

        # Assert
        assert service_result["status"] == "healthy"
        assert db_result["status"] == "connected"
        assert report_result["executive_summary"]["overall_status"] == "healthy"
        
        # Verificar que todos los métodos fueron llamados
        client_domain_service.health.check_service_health.assert_called_once()
        client_domain_service.health.check_database_connectivity.assert_called_once()
        client_domain_service.health.generate_health_report.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_operations_error_handling_chain(self, client_domain_service):
        """Test manejo de errores en cadena de operaciones de salud."""
        # Arrange
        client_domain_service.health.check_service_health.side_effect = BusinessLogicError(
            message="Service health check failed"
        )
        
        client_domain_service.health.check_database_connectivity.side_effect = BusinessLogicError(
            message="Database connectivity check failed"
        )
        
        client_domain_service.health.generate_health_report.side_effect = BusinessLogicError(
            message="Health report generation failed"
        )

        # Act & Assert
        with pytest.raises(BusinessLogicError) as exc_info:
            await client_domain_service.check_service_health()
        assert "Service health check failed" in str(exc_info.value)
        
        with pytest.raises(BusinessLogicError) as exc_info:
            await client_domain_service.check_database_connectivity()
        assert "Database connectivity check failed" in str(exc_info.value)
        
        with pytest.raises(BusinessLogicError) as exc_info:
            await client_domain_service.generate_health_report()
        assert "Health report generation failed" in str(exc_info.value)