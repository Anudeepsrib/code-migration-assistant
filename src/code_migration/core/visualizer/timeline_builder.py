"""
Timeline visualization builder.

Creates migration timeline visualizations:
- Gantt chart style timelines
- Progress tracking
- Milestone visualization
- Export capabilities
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .migration_planner import MigrationPlan


class TimelineBuilder:
    """
    Build migration timeline visualizations.
    
    Features:
    - Gantt chart timelines
    - Progress tracking
    - Milestone markers
    - Interactive timeline
    - Export to HTML/JSON
    """
    
    def __init__(self, migration_plan: MigrationPlan):
        """
        Initialize timeline builder.
        
        Args:
            migration_plan: Migration plan to visualize
        """
        self.plan = migration_plan
        self.start_date: Optional[datetime] = None
        self.wave_durations: List[float] = []
        self.milestones: List[Dict] = []
    
    def calculate_timeline(
        self, 
        start_date: Optional[datetime] = None,
        hours_per_day: float = 8.0,
        work_days_only: bool = True
    ) -> Dict:
        """
        Calculate migration timeline.
        
        Args:
            start_date: Start date for migration
            hours_per_day: Working hours per day
            work_days_only: Skip weekends if True
            
        Returns:
            Dict with timeline data
        """
        if start_date is None:
            self.start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        else:
            self.start_date = start_date
        
        # Calculate duration for each wave
        self.wave_durations = []
        current_date = self.start_date
        
        for i, wave in enumerate(self.plan.waves):
            # Estimate wave duration (simplified)
            file_count = len(wave)
            wave_hours = file_count * 0.5  # 30 minutes per file base
            
            # Add complexity multiplier
            if i > 0:  # Not first wave
                wave_hours *= 1.2  # 20% more time for dependencies
            
            # Calculate end date
            wave_end = self._add_work_hours(current_date, wave_hours, hours_per_day, work_days_only)
            
            self.wave_durations.append({
                'wave_index': i,
                'start': current_date,
                'end': wave_end,
                'duration_hours': wave_hours,
                'file_count': file_count,
                'files': wave
            })
            
            current_date = wave_end + timedelta(hours=1)  # 1 hour break between waves
        
        # Add milestones
        self._generate_milestones()
        
        return {
            'start_date': self.start_date.isoformat(),
            'end_date': current_date.isoformat(),
            'total_duration_hours': sum(w['duration_hours'] for w in self.wave_durations),
            'waves': self.wave_durations,
            'milestones': self.milestones
        }
    
    def _add_work_hours(
        self, 
        start_date: datetime, 
        hours: float,
        hours_per_day: float,
        work_days_only: bool
    ) -> datetime:
        """
        Add work hours to a date, respecting work hours and weekends.
        
        Args:
            start_date: Starting date
            hours: Hours to add
            hours_per_day: Working hours per day
            work_days_only: Skip weekends
            
        Returns:
            End date with hours added
        """
        current = start_date
        remaining_hours = hours
        
        while remaining_hours > 0:
            # Skip weekends if work_days_only
            if work_days_only and current.weekday() >= 5:  # Saturday or Sunday
                current = current.replace(hour=0, minute=0, second=0, microsecond=0)
                current += timedelta(days=1)
                current = current.replace(hour=9, minute=0, second=0, microsecond=0)
                continue
            
            # Check if within work hours (9 AM - 5 PM)
            work_start = current.replace(hour=9, minute=0, second=0, microsecond=0)
            work_end = current.replace(hour=17, minute=0, second=0, microsecond=0)
            
            if current < work_start:
                current = work_start
            elif current >= work_end:
                # Move to next day
                current = current.replace(hour=0, minute=0, second=0, microsecond=0)
                current += timedelta(days=1)
                current = current.replace(hour=9, minute=0, second=0, microsecond=0)
                continue
            
            # Calculate available work time today
            available_today = (work_end - current).total_seconds() / 3600
            
            if remaining_hours <= available_today:
                current += timedelta(hours=remaining_hours)
                remaining_hours = 0
            else:
                current = work_end
                remaining_hours -= available_today
        
        return current
    
    def _generate_milestones(self) -> None:
        """Generate migration milestones."""
        self.milestones = []
        
        # Start milestone
        self.milestones.append({
            'title': 'Migration Start',
            'date': self.start_date.isoformat(),
            'type': 'start',
            'description': f'Start {self.plan.migration_type} migration'
        })
        
        # Wave completion milestones
        for wave in self.wave_durations:
            self.milestones.append({
                'title': f'Wave {wave["wave_index"] + 1} Complete',
                'date': wave['end'].isoformat(),
                'type': 'milestone',
                'description': f'Completed {wave["file_count"]} files'
            })
        
        # End milestone
        if self.wave_durations:
            self.milestones.append({
                'title': 'Migration Complete',
                'date': self.wave_durations[-1]['end'].isoformat(),
                'type': 'end',
                'description': f'{self.plan.migration_type} migration completed'
            })
    
    def generate_gantt_chart(self, output_path: Path) -> None:
        """
        Generate interactive Gantt chart visualization.
        
        Args:
            output_path: Path to save HTML visualization
        """
        timeline_data = self.calculate_timeline()
        
        # Prepare data for D3.js
        gantt_data = {
            'metadata': {
                'title': f'{self.plan.migration_type} Migration Timeline',
                'start_date': timeline_data['start_date'],
                'end_date': timeline_data['end_date'],
                'total_duration': timeline_data['total_duration_hours']
            },
            'tasks': [],
            'milestones': timeline_data['milestones']
        }
        
        # Convert waves to tasks
        for wave in timeline_data['waves']:
            gantt_data['tasks'].append({
                'id': f'wave-{wave["wave_index"]}',
                'name': f'Wave {wave["wave_index"] + 1}',
                'start': wave['start'].isoformat(),
                'end': wave['end'].isoformat(),
                'duration': wave['duration_hours'],
                'progress': 0,  # Will be updated during migration
                'dependencies': [f'wave-{wave["wave_index"] - 1}'] if wave["wave_index"] > 0 else [],
                'files': wave['files'],
                'file_count': wave['file_count']
            })
        
        # Generate HTML
        html_template = self._generate_gantt_html(gantt_data)
        
        # Write to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
    
    def _generate_gantt_html(self, gantt_data: Dict) -> str:
        """Generate HTML template for Gantt chart."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{gantt_data['metadata']['title']}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ 
            margin: 0; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
        }}
        .chart {{ 
            margin: 20px; 
        }}
        .task-bar {{ 
            fill: #4CAF50; 
            stroke: #2E7D32;
            stroke-width: 1px;
            cursor: pointer;
        }}
        .task-bar:hover {{ 
            fill: #66BB6A; 
        }}
        .task-label {{ 
            font-size: 12px; 
            fill: #333;
        }}
        .milestone {{ 
            fill: #FF9800; 
            stroke: #F57C00;
            stroke-width: 2px;
        }}
        .grid {{ 
            stroke: #ddd; 
            stroke-width: 1px;
        }}
        .axis {{ 
            font-size: 12px; 
        }}
        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
        }}
        .header {{
            background: white;
            padding: 20px;
            margin: 0;
            border-bottom: 1px solid #ddd;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin-top: 10px;
        }}
        .stat {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
        }}
        .stat-label {{
            font-size: 11px;
            color: #666;
        }}
        .stat-value {{
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{gantt_data['metadata']['title']}</h1>
        <div class="stats">
            <div class="stat">
                <div class="stat-label">Start Date</div>
                <div class="stat-value">{gantt_data['metadata']['start_date'][:10]}</div>
            </div>
            <div class="stat">
                <div class="stat-label">End Date</div>
                <div class="stat-value">{gantt_data['metadata']['end_date'][:10]}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Total Duration</div>
                <div class="stat-value">{gantt_data['metadata']['total_duration']:.1f}h</div>
            </div>
        </div>
    </div>
    
    <div class="chart" id="gantt-chart"></div>
    <div class="tooltip"></div>
    
    <script>
        const ganttData = {json.dumps(gantt_data, indent=2)};
        
        // Parse dates
        const parseDate = d3.isoParse;
        ganttData.tasks.forEach(task => {{
            task.start = parseDate(task.start);
            task.end = parseDate(task.end);
        }});
        ganttData.milestones.forEach(milestone => {{
            milestone.date = parseDate(milestone.date);
        }});
        
        // Chart dimensions
        const margin = {{top: 20, right: 200, bottom: 30, left: 150}};
        const width = window.innerWidth - margin.left - margin.right;
        const height = ganttData.tasks.length * 60 + margin.top + margin.bottom;
        
        // Time scale
        const timeScale = d3.scaleTime()
            .domain([
                d3.min(ganttData.tasks, d => d.start),
                d3.max(ganttData.tasks, d => d.end)
            ])
            .range([0, width]);
        
        // Task scale
        const taskScale = d3.scaleBand()
            .domain(ganttData.tasks.map(d => d.id))
            .range([0, height])
            .padding(0.2);
        
        // Create SVG
        const svg = d3.select("#gantt-chart")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${{margin.left}},${{margin.top}})`);
        
        // Grid lines
        svg.selectAll(".grid")
            .data(timeScale.ticks())
            .enter().append("line")
            .attr("class", "grid")
            .attr("x1", d => timeScale(d))
            .attr("x2", d => timeScale(d))
            .attr("y1", 0)
            .attr("y2", height);
        
        // Task bars
        const taskBars = svg.selectAll(".task-bar")
            .data(ganttData.tasks)
            .enter().append("rect")
            .attr("class", "task-bar")
            .attr("x", d => timeScale(d.start))
            .attr("y", d => taskScale(d.id))
            .attr("width", d => timeScale(d.end) - timeScale(d.start))
            .attr("height", taskScale.bandwidth())
            .attr("rx", 3);
        
        // Task labels
        svg.selectAll(".task-label")
            .data(ganttData.tasks)
            .enter().append("text")
            .attr("class", "task-label")
            .attr("x", -10)
            .attr("y", d => taskScale(d.id) + taskScale.bandwidth() / 2)
            .attr("text-anchor", "end")
            .attr("dy", "0.35em")
            .text(d => d.name);
        
        // Progress bars (initially hidden)
        svg.selectAll(".progress-bar")
            .data(ganttData.tasks)
            .enter().append("rect")
            .attr("class", "progress-bar")
            .attr("x", d => timeScale(d.start))
            .attr("y", d => taskScale(d.id) + 2)
            .attr("width", d => (timeScale(d.end) - timeScale(d.start)) * d.progress / 100)
            .attr("height", taskScale.bandwidth() - 4)
            .attr("fill", "#2196F3")
            .attr("opacity", 0.7);
        
        // Milestones
        svg.selectAll(".milestone")
            .data(ganttData.milestones)
            .enter().append("polygon")
            .attr("class", "milestone")
            .attr("points", d => {{
                const x = timeScale(d.date);
                const y = height / 2;
                return `${{x}},${{y-8}} ${{x+8}},${{y}} ${{x}},${{y+8}} ${{x-8}},${{y}}`;
            }});
        
        // X-axis
        svg.append("g")
            .attr("class", "axis")
            .attr("transform", `translate(0,${{height}})`)
            .call(d3.axisBottom(timeScale).tickFormat(d3.timeFormat("%m/%d")));
        
        // Tooltip
        const tooltip = d3.select(".tooltip");
        
        taskBars.on("mouseover", function(event, d) {{
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
            tooltip.html(`
                <strong>${{d.name}}</strong><br/>
                Start: ${{d.start.toLocaleDateString()}}<br/>
                End: ${{d.end.toLocaleDateString()}}<br/>
                Duration: ${{d.duration.toFixed(1)}} hours<br/>
                Files: ${{d.file_count}}<br/>
                Progress: ${{d.progress}}%
            `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
        }})
        .on("mouseout", function(d) {{
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        }});
    </script>
</body>
</html>"""
    
    def update_progress(self, wave_index: int, progress_percentage: float) -> None:
        """
        Update progress for a specific wave.
        
        Args:
            wave_index: Wave to update
            progress_percentage: Progress percentage (0-100)
        """
        if 0 <= wave_index < len(self.wave_durations):
            self.wave_durations[wave_index]['progress'] = min(100, max(0, progress_percentage))
    
    def export_timeline(self, output_path: Path) -> None:
        """
        Export timeline data as JSON.
        
        Args:
            output_path: Path to save timeline data
        """
        timeline_data = self.calculate_timeline()
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(timeline_data, f, indent=2, default=str)
    
    def generate_timeline_report(self) -> str:
        """
        Generate formatted timeline report.
        
        Returns:
            Formatted report string
        """
        if not self.wave_durations:
            return "❌ No timeline calculated. Call calculate_timeline() first."
        
        report_lines = [
            "📅 MIGRATION TIMELINE",
            "=" * 50,
            "",
            f"📁 Project: {self.plan.project_path}",
            f"🔄 Migration Type: {self.plan.migration_type}",
            f"📅 Start Date: {self.start_date.strftime('%Y-%m-%d %H:%M')}",
            "",
            "📊 TIMELINE SUMMARY:",
            f"  Total Duration: {sum(w['duration_hours'] for w in self.wave_durations):.1f} hours",
            f"  Total Waves: {len(self.wave_durations)}",
            f"  Total Files: {sum(w['file_count'] for w in self.wave_durations)}",
            ""
        ]
        
        # Wave details
        report_lines.append("🌊 WAVE SCHEDULE:")
        for wave in self.wave_durations:
            report_lines.extend([
                f"  Wave {wave['wave_index'] + 1}:",
                f"    Start: {wave['start'].strftime('%Y-%m-%d %H:%M')}",
                f"    End: {wave['end'].strftime('%Y-%m-%d %H:%M')}",
                f"    Duration: {wave['duration_hours']:.1f} hours",
                f"    Files: {wave['file_count']}",
                ""
            ])
        
        # Milestones
        if self.milestones:
            report_lines.extend([
                "🎯 MILESTONES:",
                *[f"  {m['title']}: {m['date'][:10]}" for m in self.milestones],
                ""
            ])
        
        return "\n".join(report_lines)
