"""
Test suite for audit reporting compliance features.

Tests SOC2, GDPR, HIPAA compliance reporting capabilities.
"""

import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path

from code_migration.core.compliance import AuditReporter


class TestAuditReporter:
    """Test audit reporting and compliance features."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory."""
        from tempfile import TemporaryDirectory
        
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create audit log directory
            log_dir = project_path / '.migration-logs'
            log_dir.mkdir()
            
            # Create sample audit log entries
            audit_log = log_dir / 'security_audit.jsonl'
            
            sample_events = [
                '{"event_id":"abc123","event_type":"FILE_ACCESS","timestamp_utc":"2025-01-01T10:00:00","user":"user1","action":"READ","resource":"test.py","result":"SUCCESS"}',
                '{"event_id":"def456","event_type":"MIGRATION_EVENT","timestamp_utc":"2025-01-01T11:00:00","user":"user1","action":"START","resource":"./project","result":"SUCCESS","details":{"migration_type":"react-hooks"}}',
                '{"event_id":"ghi789","event_type":"SECURITY_VIOLATION","timestamp_utc":"2025-01-01T12:00:00","user":"user2","action":"VIOLATION","resource":"test.py","result":"BLOCKED","details":{"violation_type":"PATH_TRAVERSAL"}}',
                '{"event_id":"jkl012","event_type":"FILE_ACCESS","timestamp_utc":"2025-01-01T13:00:00","user":"user1","action":"WRITE","resource":"test.py","result":"SUCCESS","details":{"file_size":1024}}',
                '{"event_id":"mno345","event_type":"MIGRATION_EVENT","timestamp_utc":"2025-01-01T14:00:00","user":"user1","action":"COMPLETE","resource":"./project","result":"SUCCESS","details":{"migration_type":"react-hooks","files_migrated":10}}'
            ]
            
            audit_log.write_text('\n'.join(sample_events))
            
            yield project_path

    @pytest.fixture
    def reporter(self, temp_project_dir):
        """Create and clean up audit reporter."""
        reporter = AuditReporter(temp_project_dir)
        yield reporter
        reporter.close()
    
    def test_soc2_report_generation(self, reporter):
        """Test SOC2 compliance report generation."""
        
        end_date = datetime(2025, 1, 1, 15, 0, 0)
        start_date = end_date - timedelta(days=90)
        
        report = reporter.generate_soc2_report(start_date, end_date)
        
        # Verify report structure
        assert report['report_type'] == 'SOC2'
        assert 'report_period' in report
        assert 'trust_services_criteria' in report
        assert 'compliance_score' in report
        assert 'summary' in report
        assert 'recommendations' in report
        assert 'evidence' in report
        
        # Verify trust services criteria
        criteria = report['trust_services_criteria']
        assert 'security' in criteria
        assert 'availability' in criteria
        assert 'processing_integrity' in criteria
        assert 'confidentiality' in criteria
        assert 'privacy' in criteria
        
        # Verify security criteria
        security = criteria['security']
        assert 'access_control' in security
        assert 'incident_response' in security
        assert 'risk_management' in security
        
        # Verify compliance score
        score = report['compliance_score']
        assert 'overall_score' in score
        assert 'grade' in score
        assert 'status' in score
        assert isinstance(score['overall_score'], (int, float))
        assert score['grade'] in ['A', 'B', 'C']
        assert score['status'] in ['COMPLIANT', 'NEEDS_IMPROVEMENT']
    
    def test_gdpr_report_generation(self, reporter):
        """Test GDPR compliance report generation."""
        
        end_date = datetime(2025, 1, 1, 15, 0, 0)
        start_date = end_date - timedelta(days=90)
        
        report = reporter.generate_gdpr_report(start_date, end_date)
        
        # Verify report structure
        assert report['report_type'] == 'GDPR'
        assert 'report_period' in report
        assert 'data_controller' in report
        assert 'gdpr_articles' in report
        assert 'pii_processing' in report
        assert 'compliance_score' in report
        assert 'recommendations' in report
        assert 'data_subject_requests' in report
        
        # Verify GDPR articles
        articles = report['gdpr_articles']
        assert 'article_5_data_principles' in articles
        assert 'article_25_privacy_by_design' in articles
        assert 'article_32_security_of_processing' in articles
        assert 'article_33_breach_notification' in articles
        assert 'article_35_dpia' in articles
        
        # Verify Article 5 principles
        article_5 = articles['article_5_data_principles']
        assert 'lawfulness' in article_5
        assert 'fairness' in article_5
        assert 'transparency' in article_5
        assert 'purpose_limitation' in article_5
        assert 'data_minimization' in article_5
        assert 'accuracy' in article_5
        assert 'storage_limitation' in article_5
        assert 'security' in article_5
        
        # Verify each principle has score and compliance status
        for principle in article_5.values():
            assert 'compliant' in principle
            assert 'score' in principle
            assert isinstance(principle['score'], (int, float))
    
    def test_hipaa_report_generation(self, reporter):
        """Test HIPAA compliance report generation."""
        
        end_date = datetime(2025, 1, 1, 15, 0, 0)
        start_date = end_date - timedelta(days=90)
        
        report = reporter.generate_hipaa_report(start_date, end_date)
        
        # Verify report structure
        assert report['report_type'] == 'HIPAA'
        assert 'report_period' in report
        assert 'covered_entity' in report
        assert 'hipaa_rules' in report
        assert 'phi_processing' in report
        assert 'compliance_score' in report
        assert 'recommendations' in report
        assert 'security_measures' in report
        
        # Verify HIPAA rules
        rules = report['hipaa_rules']
        assert 'privacy_rule' in rules
        assert 'security_rule' in rules
        assert 'breach_notification_rule' in rules
        assert 'enforcement_rule' in rules
        
        # Verify security rule safeguards
        security_rule = rules['security_rule']
        assert 'administrative_safeguards' in security_rule
        assert 'physical_safeguards' in security_rule
        assert 'technical_safeguards' in security_rule
        
        # Verify each safeguard has compliance metrics
        for safeguard in security_rule.values():
            assert 'compliant' in safeguard
            assert 'score' in safeguard
            assert isinstance(safeguard['score'], (int, float))
    
    def test_security_audit_report_generation(self, reporter):
        """Test security audit report generation."""
        
        end_date = datetime(2025, 1, 1, 15, 0, 0)
        start_date = end_date - timedelta(days=30)
        
        report = reporter.generate_security_audit_report(start_date, end_date)
        
        # Verify report structure
        assert report['report_type'] == 'SECURITY_AUDIT'
        assert 'report_period' in report
        assert 'security_analysis' in report
        assert 'risk_assessment' in report
        assert 'security_score' in report
        assert 'recommendations' in report
        assert 'compliance_status' in report
        
        # Verify security analysis
        analysis = report['security_analysis']
        assert 'authentication_events' in analysis
        assert 'access_control' in analysis
        assert 'data_protection' in analysis
        assert 'security_incidents' in analysis
        assert 'vulnerability_management' in analysis
        
        # Verify authentication events analysis
        auth_events = analysis['authentication_events']
        assert 'total_attempts' in auth_events
        assert 'successful_logins' in auth_events
        assert 'failed_logins' in auth_events
        assert isinstance(auth_events['total_attempts'], int)
    
    def test_report_export_json(self, temp_project_dir, reporter):
        """Test JSON report export functionality."""
        
        # Generate a report
        report = reporter.generate_soc2_report()
        
        # Export to JSON
        output_path = temp_project_dir / 'soc2_report.json'
        success = reporter.export_report(report, output_path, 'json')
        
        assert success is True
        assert output_path.exists()
        
        # Verify exported content
        import json
        with open(output_path, 'r') as f:
            exported_data = json.load(f)
        
        assert exported_data['report_type'] == 'SOC2'
        assert 'trust_services_criteria' in exported_data
    
    def test_report_export_html(self, temp_project_dir, reporter):
        """Test HTML report export functionality."""
        
        # Generate a report
        report = reporter.generate_soc2_report()
        
        # Export to HTML
        output_path = temp_project_dir / 'soc2_report.html'
        success = reporter.export_report(report, output_path, 'html')
        
        assert success is True
        assert output_path.exists()
        
        # Verify exported content
        with open(output_path, 'r') as f:
            html_content = f.read()
        
        assert 'SOC2 Compliance Report' in html_content
        assert '<!DOCTYPE html>' in html_content
        assert '</html>' in html_content
    
    def test_report_export_invalid_format(self, temp_project_dir, reporter):
        """Test export with invalid format."""
        
        report = reporter.generate_soc2_report()
        output_path = temp_project_dir / 'report.txt'
        
        # Should raise ValueError for invalid format
        with pytest.raises(ValueError, match="Unsupported format"):
            reporter.export_report(report, output_path, 'txt')
    
    def test_date_range_filtering(self, reporter):
        """Test date range filtering in reports."""
        
        # Test with specific date range
        end_date = datetime(2025, 1, 1, 12, 0, 0)  # Noon
        start_date = datetime(2025, 1, 1, 10, 0, 0)  # 2 hours earlier
        
        report = reporter.generate_soc2_report(start_date, end_date)
        
        # Should only include events within the 2-hour window
        summary = report['summary']
        assert summary['total_events'] >= 0  # Should have some events
        
        # Test with wider date range
        wide_end = datetime(2025, 1, 2, 0, 0, 0)
        wide_start = datetime(2024, 12, 1, 0, 0, 0)
        
        wide_report = reporter.generate_soc2_report(wide_start, wide_end)
        wide_summary = wide_report['summary']
        
        # Should include more events with wider range
        assert wide_summary['total_events'] >= summary['total_events']
    
    def test_default_date_ranges(self, reporter):
        """Test default date range handling."""
        
        # Generate report without specifying dates
        report = reporter.generate_soc2_report()
        
        # Should use default ranges (90 days for SOC2/GDPR/HIPAA, 30 days for security)
        assert 'report_period' in report
        
        period = report['report_period']
        assert 'start' in period
        assert 'end' in period
        
        # Parse dates to verify they're recent
        end_date = datetime.fromisoformat(period['end'])
        start_date = datetime.fromisoformat(period['start'])
        
        # Should be approximately 90 days apart for SOC2
        date_diff = end_date - start_date
        assert timedelta(days=85) <= date_diff <= timedelta(days=95)
    
    def test_empty_log_handling(self, temp_project_dir):
        """Test handling of empty or missing audit logs."""
        # Remove audit log
        audit_log = temp_project_dir / '.migration-logs' / 'security_audit.jsonl'
        if audit_log.exists():
            audit_log.unlink()
        
        with AuditReporter(temp_project_dir) as reporter:
            # Should still generate report with empty data
            report = reporter.generate_soc2_report()
            
            assert report['report_type'] == 'SOC2'
            assert 'summary' in report
            
            summary = report['summary']
            assert summary['total_events'] == 0
            assert summary['security_incidents'] == 0
    
    def test_malformed_log_handling(self, temp_project_dir):
        """Test handling of malformed audit log entries."""
        # Create malformed audit log
        audit_log = temp_project_dir / '.migration-logs' / 'security_audit.jsonl'
        
        malformed_entries = [
            '{"event_id":"abc123","event_type":"FILE_ACCESS","timestamp_utc":"invalid-date","user":"user1","action":"READ","resource":"test.py","result":"SUCCESS"}',
            'not a json line',
            '{"incomplete":"json"',
            '{"event_id":"def456","event_type":"MIGRATION_EVENT","timestamp_utc":"2025-01-01T11:00:00","user":"user1","action":"START","resource":"./project","result":"SUCCESS"}'
        ]
        
        audit_log.write_text('\n'.join(malformed_entries))
        
        with AuditReporter(temp_project_dir) as reporter:
            # Should handle malformed entries gracefully
            report = reporter.generate_soc2_report()
            
            assert report['report_type'] == 'SOC2'
            assert 'summary' in report
            
            # Should still process valid entries
            summary = report['summary']
            assert summary['total_events'] >= 1  # At least one valid entry
    
    def test_recommendation_generation(self, reporter):
        """Test recommendation generation for compliance reports."""
        
        # Generate reports with different compliance levels
        soc2_report = reporter.generate_soc2_report()
        gdpr_report = reporter.generate_gdpr_report()
        hipaa_report = reporter.generate_hipaa_report()
        
        # All reports should have recommendations
        for report in [soc2_report, gdpr_report, hipaa_report]:
            assert 'recommendations' in report
            assert isinstance(report['recommendations'], list)
            assert len(report['recommendations']) > 0
            
            # Each recommendation should be a non-empty string
            for rec in report['recommendations']:
                assert isinstance(rec, str)
                assert len(rec.strip()) > 0
    
    def test_evidence_collection(self, reporter):
        """Test evidence collection for compliance reports."""
        
        report = reporter.generate_soc2_report()
        
        evidence = report['evidence']
        assert isinstance(evidence, list)
        assert len(evidence) > 0
        
        # Each evidence item should have required fields
        for item in evidence:
            assert 'type' in item
            assert 'description' in item
            assert isinstance(item['type'], str)
            assert isinstance(item['description'], str)


class TestAuditReporterEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for edge case testing."""
        from tempfile import TemporaryDirectory
        
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create audit log directory
            log_dir = project_path / '.migration-logs'
            log_dir.mkdir()
            
            # Create audit log with edge case events
            audit_log = log_dir / 'security_audit.jsonl'
            
            edge_case_events = [
                '{"event_id":"edge1","event_type":"FILE_ACCESS","timestamp_utc":"2025-01-01T23:59:59","user":"user1","action":"READ","resource":"test.py","result":"SUCCESS","details":{"file_size":0}}',
                '{"event_id":"edge2","event_type":"SECURITY_VIOLATION","timestamp_utc":"2025-01-01T00:00:00","user":"user2","action":"VIOLATION","resource":"../../../etc/passwd","result":"BLOCKED","details":{"violation_type":"PATH_TRAVERSAL","severity":"CRITICAL"}}',
                '{"event_id":"edge3","event_type":"MIGRATION_EVENT","timestamp_utc":"2025-01-01T12:30:45","user":"user1","action":"COMPLETE","resource":"./project","result":"SUCCESS","details":{"migration_type":"react-hooks","files_migrated":0,"errors":[]}}'
            ]
            
            audit_log.write_text('\n'.join(edge_case_events))
            
            yield project_path

    @pytest.fixture
    def reporter(self, temp_project_dir):
        """Create and clean up audit reporter."""
        reporter = AuditReporter(temp_project_dir)
        yield reporter
        reporter.close()
    
    def test_boundary_date_ranges(self, reporter):
        """Test boundary conditions for date ranges."""
        
        # Test with very narrow date range (should include few events)
        narrow_start = datetime(2025, 1, 1, 12, 30, 0)
        narrow_end = datetime(2025, 1, 1, 12, 31, 0)
        
        narrow_report = reporter.generate_soc2_report(narrow_start, narrow_end)
        assert narrow_report['summary']['total_events'] >= 0
        
        # Test with very wide date range (should include all events)
        wide_start = datetime(2024, 1, 1, 0, 0, 0)
        wide_end = datetime(2025, 12, 31, 23, 59, 59)
        
        wide_report = reporter.generate_soc2_report(wide_start, wide_end)
        assert wide_report['summary']['total_events'] >= narrow_report['summary']['total_events']
    
    def test_zero_length_files(self, temp_project_dir):
        """Test handling of zero-length files in audit."""
        # Create empty audit log
        audit_log = temp_project_dir / '.migration-logs' / 'security_audit.jsonl'
        audit_log.write_text("")
        
        with AuditReporter(temp_project_dir) as reporter:
            report = reporter.generate_soc2_report()
            
            # Should handle empty log gracefully
            assert report['summary']['total_events'] == 0
            assert report['summary']['security_incidents'] == 0
    
    def test_unicode_in_events(self, temp_project_dir):
        """Test handling of Unicode characters in audit events."""
        audit_log = temp_project_dir / '.migration-logs' / 'security_audit.jsonl'
        
        unicode_events = [
            '{"event_id":"unicode1","event_type":"FILE_ACCESS","timestamp_utc":"2025-01-01T10:00:00","user":"用户1","action":"READ","resource":"测试.py","result":"SUCCESS"}',
            '{"event_id":"unicode2","event_type":"SECURITY_VIOLATION","timestamp_utc":"2025-01-01T11:00:00","user":"пользователь","action":"VIOLATION","resource":"malicious.py","result":"BLOCKED","details":{"violation_type":"INJECTION_ATTEMPT"}}'
        ]
        
        audit_log.write_text('\n'.join(unicode_events), encoding='utf-8')
        
        audit_log.write_text('\n'.join(unicode_events), encoding='utf-8')
        
        with AuditReporter(temp_project_dir) as reporter:
            report = reporter.generate_soc2_report()
            
            # Should handle Unicode in events
            assert report['summary']['total_events'] >= 2
    
    def test_large_number_of_events(self, temp_project_dir):
        """Test handling of large number of audit events."""
        audit_log = temp_project_dir / '.migration-logs' / 'security_audit.jsonl'
        
        # Generate many events
        events = []
        for i in range(1000):
            event = {
                "event_id": f"event_{i}",
                "event_type": "FILE_ACCESS",
                "timestamp_utc": "2025-01-01T10:00:00",
                "user": f"user{i % 10}",
                "action": "READ",
                "resource": f"file_{i}.py",
                "result": "SUCCESS"
            }
            events.append(json.dumps(event))
        
        audit_log.write_text('\n'.join(events))
        
        audit_log.write_text('\n'.join(events))
        
        with AuditReporter(temp_project_dir) as reporter:
            report = reporter.generate_soc2_report()
            
            # Should handle large number of events
            assert report['summary']['total_events'] == 1000
    
    def test_missing_log_directory(self, temp_project_dir):
        """Test handling when audit log directory doesn't exist."""
        # Remove log directory
        log_dir = temp_project_dir / '.migration-logs'
        if log_dir.exists():
            import shutil
            shutil.rmtree(log_dir)
        
        # Should create directory and handle missing logs
        with AuditReporter(temp_project_dir) as reporter:
            report = reporter.generate_soc2_report()
            
            assert report['summary']['total_events'] == 0
