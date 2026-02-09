"""
Interactive migration planning interface.

Provides tools for planning and managing migrations:
- Wave-based migration planning
- Interactive file selection
- Progress tracking
- Manual override capabilities
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

from .graph_generator import VisualMigrationPlanner


@dataclass
class MigrationPlan:
    """Migration plan configuration."""
    project_path: str
    migration_type: str
    waves: List[List[str]]
    metadata: Dict
    created_at: str
    estimated_duration: float
    risk_level: str


class MigrationPlanner:
    """
    Interactive migration planning tool.
    
    Features:
    - Wave-based planning
    - Manual file ordering
    - Risk assessment integration
    - Progress tracking
    - Plan export/import
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize migration planner.
        
        Args:
            project_path: Path to project to plan migration for
        """
        self.project_path = Path(project_path)
        self.visual_planner = VisualMigrationPlanner(project_path)
        self.current_plan: Optional[MigrationPlan] = None
    
    def create_migration_plan(
        self, 
        migration_type: str,
        manual_waves: Optional[List[List[str]]] = None,
        risk_tolerance: str = "MEDIUM"
    ) -> MigrationPlan:
        """
        Create migration plan.
        
        Args:
            migration_type: Type of migration to plan
            manual_waves: Manually specified waves (optional)
            risk_tolerance: Risk tolerance level (LOW, MEDIUM, HIGH)
            
        Returns:
            MigrationPlan with detailed configuration
        """
        from datetime import datetime
        
        # Build dependency graph
        self.visual_planner.build_dependency_graph()
        
        # Calculate waves (use manual if provided)
        if manual_waves:
            waves = manual_waves
        else:
            waves = self.visual_planner.calculate_migration_waves()
        
        # Get graph statistics
        stats = self.visual_planner.get_graph_statistics()
        
        # Estimate duration (rough calculation)
        total_files = sum(len(wave) for wave in waves)
        base_duration = total_files * 0.5  # 30 minutes per file
        
        # Adjust based on complexity
        if stats.get('circular_dependencies', False):
            base_duration *= 1.5  # 50% more time for circular deps
        
        # Determine risk level
        if stats.get('circular_dependencies', False) or stats.get('density', 0) > 0.3:
            risk_level = "HIGH"
        elif stats.get('average_degree', 0) > 5:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Create plan
        plan = MigrationPlan(
            project_path=str(self.project_path),
            migration_type=migration_type,
            waves=waves,
            metadata={
                'statistics': stats,
                'risk_tolerance': risk_tolerance,
                'total_files': total_files,
                'total_waves': len(waves)
            },
            created_at=datetime.now().isoformat(),
            estimated_duration=base_duration,
            risk_level=risk_level
        )
        
        self.current_plan = plan
        return plan
    
    def modify_wave_order(self, current_wave: int, new_position: int) -> bool:
        """
        Reorder migration waves.
        
        Args:
            current_wave: Current wave index
            new_position: New position index
            
        Returns:
            True if successful
        """
        if not self.current_plan:
            return False
        
        if current_wave < 0 or current_wave >= len(self.current_plan.waves):
            return False
        
        if new_position < 0 or new_position >= len(self.current_plan.waves):
            return False
        
        # Reorder waves
        waves = self.current_plan.waves
        wave = waves.pop(current_wave)
        waves.insert(new_position, wave)
        
        self.current_plan.waves = waves
        return True
    
    def move_file_between_waves(self, file_path: str, from_wave: int, to_wave: int) -> bool:
        """
        Move a file between waves.
        
        Args:
            file_path: File to move
            from_wave: Source wave index
            to_wave: Target wave index
            
        Returns:
            True if successful
        """
        if not self.current_plan:
            return False
        
        waves = self.current_plan.waves
        
        if from_wave < 0 or from_wave >= len(waves):
            return False
        
        if to_wave < 0 or to_wave >= len(waves):
            return False
        
        # Remove file from source wave
        if file_path in waves[from_wave]:
            waves[from_wave].remove(file_path)
            waves[to_wave].append(file_path)
            return True
        
        return False
    
    def add_file_to_wave(self, file_path: str, wave_index: int) -> bool:
        """
        Add a file to a specific wave.
        
        Args:
            file_path: File to add
            wave_index: Target wave index
            
        Returns:
            True if successful
        """
        if not self.current_plan:
            return False
        
        if wave_index < 0 or wave_index >= len(self.current_plan.waves):
            return False
        
        # Check if file already exists in any wave
        for wave in self.current_plan.waves:
            if file_path in wave:
                return False
        
        self.current_plan.waves[wave_index].append(file_path)
        return True
    
    def remove_file_from_plan(self, file_path: str) -> bool:
        """
        Remove a file from the migration plan.
        
        Args:
            file_path: File to remove
            
        Returns:
            True if successful
        """
        if not self.current_plan:
            return False
        
        for wave in self.current_plan.waves:
            if file_path in wave:
                wave.remove(file_path)
                return True
        
        return False
    
    def get_wave_details(self, wave_index: int) -> Optional[Dict]:
        """
        Get details for a specific wave.
        
        Args:
            wave_index: Wave index
            
        Returns:
            Dict with wave details
        """
        if not self.current_plan:
            return None
        
        if wave_index < 0 or wave_index >= len(self.current_plan.waves):
            return None
        
        wave_files = self.current_plan.waves[wave_index]
        
        # Calculate file statistics
        total_lines = 0
        total_complexity = 0
        
        for file_path in wave_files:
            try:
                full_path = self.project_path / file_path
                if full_path.exists():
                    content = full_path.read_text(encoding='utf-8', errors='ignore')
                    total_lines += len(content.splitlines())
                    # Basic complexity estimation (simplified)
                    total_complexity += content.count('if') + content.count('for') + content.count('while')
            except Exception:
                continue
        
        return {
            'wave_index': wave_index,
            'file_count': len(wave_files),
            'files': wave_files,
            'total_lines': total_lines,
            'estimated_hours': total_lines / 1000,  # Rough estimate
            'average_lines_per_file': total_lines / max(len(wave_files), 1)
        }
    
    def validate_plan(self) -> Dict:
        """
        Validate migration plan for issues.
        
        Returns:
            Dict with validation results
        """
        if not self.current_plan:
            return {'valid': False, 'errors': ['No migration plan loaded']}
        
        errors = []
        warnings = []
        
        # Check for empty waves
        for i, wave in enumerate(self.current_plan.waves):
            if not wave:
                warnings.append(f'Wave {i + 1} is empty')
        
        # Check for duplicate files
        all_files = []
        for i, wave in enumerate(self.current_plan.waves):
            for file_path in wave:
                if file_path in all_files:
                    errors.append(f'File {file_path} appears in multiple waves')
                all_files.append(file_path)
        
        # Check if files exist
        for file_path in all_files:
            full_path = self.project_path / file_path
            if not full_path.exists():
                warnings.append(f'File {file_path} does not exist')
        
        # Check dependency order (basic check)
        try:
            # Rebuild graph to check dependencies
            self.visual_planner.build_dependency_graph()
            graph = self.visual_planner.graph
            
            for i, wave in enumerate(self.current_plan.waves):
                for file_path in wave:
                    # Check if file depends on files in later waves
                    if file_path in graph.nodes():
                        for successor in graph.successors(file_path):
                            for j, later_wave in enumerate(self.current_plan.waves[i+1:], i+1):
                                if successor in later_wave:
                                    warnings.append(
                                        f'File {file_path} (Wave {i+1}) depends on {successor} (Wave {j+1})'
                                    )
        except Exception:
            warnings.append('Could not validate dependency order')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'total_files': len(all_files),
            'total_waves': len(self.current_plan.waves)
        }
    
    def export_plan(self, output_path: Path) -> bool:
        """
        Export migration plan to JSON.
        
        Args:
            output_path: Path to save plan
            
        Returns:
            True if successful
        """
        if not self.current_plan:
            return False
        
        try:
            plan_data = {
                'project_path': self.current_plan.project_path,
                'migration_type': self.current_plan.migration_type,
                'waves': self.current_plan.waves,
                'metadata': self.current_plan.metadata,
                'created_at': self.current_plan.created_at,
                'estimated_duration': self.current_plan.estimated_duration,
                'risk_level': self.current_plan.risk_level
            }
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(plan_data, f, indent=2)
            
            return True
            
        except Exception:
            return False
    
    def import_plan(self, plan_path: Path) -> bool:
        """
        Import migration plan from JSON.
        
        Args:
            plan_path: Path to plan file
            
        Returns:
            True if successful
        """
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
            
            self.current_plan = MigrationPlan(
                project_path=plan_data['project_path'],
                migration_type=plan_data['migration_type'],
                waves=plan_data['waves'],
                metadata=plan_data.get('metadata', {}),
                created_at=plan_data.get('created_at', ''),
                estimated_duration=plan_data.get('estimated_duration', 0),
                risk_level=plan_data.get('risk_level', 'MEDIUM')
            )
            
            return True
            
        except Exception:
            return False
    
    def generate_plan_report(self) -> str:
        """
        Generate formatted migration plan report.
        
        Returns:
            Formatted report string
        """
        if not self.current_plan:
            return "❌ No migration plan loaded."
        
        validation = self.validate_plan()
        
        report_lines = [
            "📋 MIGRATION PLAN REPORT",
            "=" * 50,
            "",
            f"📁 Project: {self.current_plan.project_path}",
            f"🔄 Migration Type: {self.current_plan.migration_type}",
            f"📅 Created: {self.current_plan.created_at}",
            f"⏱️  Estimated Duration: {self.current_plan.estimated_duration:.1f} hours",
            f"⚠️  Risk Level: {self.current_plan.risk_level}",
            "",
            "📊 PLAN SUMMARY:",
            f"  Total Waves: {len(self.current_plan.waves)}",
            f"  Total Files: {sum(len(wave) for wave in self.current_plan.waves)}",
            ""
        ]
        
        # Wave details
        report_lines.append("🌊 MIGRATION WAVES:")
        for i, wave in enumerate(self.current_plan.waves):
            wave_details = self.get_wave_details(i)
            if wave_details:
                report_lines.extend([
                    f"  Wave {i + 1}: {wave_details['file_count']} files "
                    f"({wave_details['estimated_hours']:.1f} hours)",
                    f"    Files: {', '.join(wave_details['files'][:5])}"
                ])
                if len(wave_details['files']) > 5:
                    report_lines.append(f"    ... and {len(wave_details['files']) - 5} more")
                report_lines.append("")
        
        # Validation results
        report_lines.extend([
            "✅ VALIDATION RESULTS:",
            f"  Status: {'✅ Valid' if validation['valid'] else '❌ Invalid'}",
            f"  Errors: {len(validation['errors'])}",
            f"  Warnings: {len(validation['warnings'])}"
        ])
        
        if validation['errors']:
            report_lines.extend(["", "🚨 ERRORS:"])
            for error in validation['errors']:
                report_lines.append(f"  • {error}")
        
        if validation['warnings']:
            report_lines.extend(["", "⚠️  WARNINGS:"])
            for warning in validation['warnings']:
                report_lines.append(f"  • {warning}")
        
        return "\n".join(report_lines)
