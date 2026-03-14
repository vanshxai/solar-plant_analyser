"""
Report Generator Module for Solar Plant Analyzer
Generates PDF and CSV reports for solar plant analysis.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import io


class ReportGenerator:
    """Generates fault reports in various formats."""
    
    def __init__(self):
        self.report_data = {}
    
    def generate_text_report(
        self,
        metrics: Dict[str, Any],
        faults: List[Dict],
        plant_info: Optional[Dict] = None
    ) -> str:
        """
        Generate a text-based report.
        
        Args:
            metrics: Efficiency metrics from analysis
            faults: List of detected faults
            plant_info: Optional plant information
            
        Returns:
            Formatted text report
        """
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("SOLAR PLANT FAULT REPORT")
        lines.append("=" * 70)
        lines.append("")
        
        # Plant Info
        lines.append("PLANT INFORMATION")
        lines.append("-" * 40)
        if plant_info:
            lines.append(f"Plant Name: {plant_info.get('name', 'N/A')}")
            lines.append(f"Plant Capacity: {plant_info.get('capacity_kw', 'N/A')} kW")
            lines.append(f"Location: {plant_info.get('location', 'N/A')}")
        else:
            lines.append("Plant Capacity: 500 kW (default)")
        lines.append(f"Analysis Date: {datetime.now().strftime('%d %B %Y %H:%M')}")
        lines.append("")
        
        # Data Summary
        lines.append("DATA SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total Data Points: {metrics.get('data_points', 'N/A')}")
        if 'date_range' in metrics:
            lines.append(f"Date Range: {metrics['date_range'].get('start', 'N/A')} to {metrics['date_range'].get('end', 'N/A')}")
        lines.append("")
        
        # Performance Summary
        lines.append("PERFORMANCE SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total Energy Generated: {metrics.get('total_energy_kwh', 0):.2f} kWh")
        lines.append(f"Average Power: {metrics.get('avg_power_kw', 0):.2f} kW")
        lines.append(f"Peak Power: {metrics.get('peak_power_kw', 0):.2f} kW")
        lines.append(f"Capacity Factor: {metrics.get('capacity_factor', 0)*100:.1f}%")
        
        if 'avg_performance_ratio' in metrics:
            lines.append(f"Average Performance Ratio: {metrics.get('avg_performance_ratio', 0)*100:.1f}%")
        
        if 'avg_voltage' in metrics:
            lines.append(f"Average Voltage: {metrics.get('avg_voltage', 0):.1f} V")
            lines.append(f"Voltage Range: {metrics.get('min_voltage', 0):.1f} V - {metrics.get('max_voltage', 0):.1f} V")
        
        if 'avg_current' in metrics:
            lines.append(f"Average Current: {metrics.get('avg_current', 0):.2f} A")
            lines.append(f"Current Range: {metrics.get('min_current', 0):.2f} A - {metrics.get('max_current', 0):.2f} A")
        
        if 'avg_temperature' in metrics:
            lines.append(f"Average Temperature: {metrics.get('avg_temperature', 0):.1f} °C")
            lines.append(f"Maximum Temperature: {metrics.get('max_temperature', 0):.1f} °C")
        
        lines.append("")
        
        # Fault Summary
        lines.append("FAULT SUMMARY")
        lines.append("-" * 40)
        
        critical_count = sum(1 for f in faults if f.get('severity') == 'critical')
        high_count = sum(1 for f in faults if f.get('severity') == 'high')
        medium_count = sum(1 for f in faults if f.get('severity') == 'medium')
        low_count = sum(1 for f in faults if f.get('severity') == 'low')
        
        lines.append(f"Total Faults Detected: {len(faults)}")
        lines.append(f"  - Critical: {critical_count}")
        lines.append(f"  - High: {high_count}")
        lines.append(f"  - Medium: {medium_count}")
        lines.append(f"  - Low: {low_count}")
        lines.append("")
        
        # Detailed Faults
        if faults:
            lines.append("DETAILED FAULT LIST")
            lines.append("-" * 40)
            
            for i, fault in enumerate(faults, 1):
                lines.append(f"\n{i}. {fault.get('fault_type', 'Unknown').replace('_', ' ').title()}")
                lines.append(f"   Severity: {fault.get('severity', 'unknown').upper()}")
                
                if fault.get('timestamp') and fault['timestamp'] != 'N/A':
                    lines.append(f"   Timestamp: {fault['timestamp']}")
                
                lines.append(f"   Description: {fault.get('description', 'N/A')}")
                lines.append(f"   Possible Cause: {fault.get('possible_cause', 'N/A')}")
                lines.append(f"   Recommended Action: {fault.get('recommended_action', 'N/A')}")
                
                if fault.get('string_id'):
                    lines.append(f"   Affected String: {fault['string_id']}")
                
                if fault.get('value') is not None:
                    lines.append(f"   Measured Value: {fault['value']:.2f}")
                
                if fault.get('threshold') is not None:
                    lines.append(f"   Threshold: {fault['threshold']:.2f}")
            
            lines.append("")
        
        # Recommendations
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 40)
        
        if critical_count > 0:
            lines.append("⚠️  IMMEDIATE ACTION REQUIRED: Critical faults detected!")
            lines.append("   - Inspect plant immediately for safety issues")
            lines.append("   - Check inverter status and grid connection")
        
        if high_count > 0:
            lines.append("⚠️  HIGH PRIORITY: Address high severity faults within 24 hours")
            lines.append("   - Schedule maintenance inspection")
            lines.append("   - Review recent weather events or grid disturbances")
        
        if medium_count > 0:
            lines.append("📋  MEDIUM PRIORITY: Plan maintenance within the week")
            lines.append("   - Check for shading or soiling issues")
            lines.append("   - Verify string connections")
        
        if low_count > 0:
            lines.append("📝  LOW PRIORITY: Monitor and address during next scheduled maintenance")
            lines.append("   - Review sensor calibration")
            lines.append("   - Log for trend analysis")
        
        if not faults:
            lines.append("✓ No faults detected. Continue regular monitoring.")
        
        lines.append("")
        lines.append("=" * 70)
        lines.append("END OF REPORT")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def generate_pdf_report(
        self,
        metrics: Dict[str, Any],
        faults: List[Dict],
        plant_info: Optional[Dict] = None,
        figures: Optional[Dict] = None
    ) -> bytes:
        """
        Generate a PDF report.
        
        Args:
            metrics: Efficiency metrics
            faults: Detected faults
            plant_info: Plant information
            figures: Optional Plotly figures to include
            
        Returns:
            PDF file as bytes
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                PageBreak, Image
            )
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            import io
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=landscape(A4),
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f77b4'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph("Solar Plant Fault Report", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Plant Info
            info_table = Table([
                ['Plant Capacity', f"{plant_info.get('capacity_kw', 500) if plant_info else 500} kW"],
                ['Analysis Date', datetime.now().strftime('%d %B %Y %H:%M')],
                ['Total Data Points', str(metrics.get('data_points', 'N/A'))],
            ], colWidths=[2*inch, 3*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Performance Summary
            story.append(Paragraph("Performance Summary", styles['Heading2']))
            perf_data = [
                ['Metric', 'Value'],
                ['Total Energy', f"{metrics.get('total_energy_kwh', 0):.2f} kWh"],
                ['Average Power', f"{metrics.get('avg_power_kw', 0):.2f} kW"],
                ['Peak Power', f"{metrics.get('peak_power_kw', 0):.2f} kW"],
                ['Capacity Factor', f"{metrics.get('capacity_factor', 0)*100:.1f}%"],
                ['Avg Performance Ratio', f"{metrics.get('avg_performance_ratio', 0)*100:.1f}%"] if 'avg_performance_ratio' in metrics else None,
            ]
            perf_data = [row for row in perf_data if row]
            
            perf_table = Table(perf_data, colWidths=[3*inch, 2*inch])
            perf_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(perf_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Fault Summary
            story.append(Paragraph("Fault Summary", styles['Heading2']))
            
            critical_count = sum(1 for f in faults if f.get('severity') == 'critical')
            high_count = sum(1 for f in faults if f.get('severity') == 'high')
            medium_count = sum(1 for f in faults if f.get('severity') == 'medium')
            low_count = sum(1 for f in faults if f.get('severity') == 'low')
            
            fault_summary = [
                ['Severity', 'Count'],
                ['Critical', str(critical_count)],
                ['High', str(high_count)],
                ['Medium', str(medium_count)],
                ['Low', str(low_count)],
                ['TOTAL', str(len(faults))]
            ]
            
            fault_table = Table(fault_summary, colWidths=[3*inch, 2*inch])
            fault_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d62728')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0'))
            ]))
            story.append(fault_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Detailed Faults
            if faults:
                story.append(Paragraph("Detailed Fault List", styles['Heading2']))
                
                for fault in faults:
                    fault_title = fault.get('fault_type', 'Unknown').replace('_', ' ').title()
                    story.append(Paragraph(f"<b>{fault_title}</b>", styles['Heading3']))
                    
                    fault_info = [
                        ['Attribute', 'Details'],
                        ['Severity', fault.get('severity', 'unknown').upper()],
                        ['Description', fault.get('description', 'N/A')],
                        ['Possible Cause', fault.get('possible_cause', 'N/A')],
                        ['Recommended Action', fault.get('recommended_action', 'N/A')]
                    ]
                    
                    if fault.get('timestamp') and fault['timestamp'] != 'N/A':
                        fault_info.insert(2, ['Timestamp', str(fault['timestamp'])])
                    
                    fault_detail_table = Table(fault_info, colWidths=[2*inch, 5*inch])
                    fault_detail_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]))
                    story.append(fault_detail_table)
                    story.append(Spacer(1, 0.2*inch))
            
            # Build PDF
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except ImportError:
            # Fallback to text report if reportlab not available
            text_report = self.generate_text_report(metrics, faults, plant_info)
            return text_report.encode('utf-8')
    
    def generate_csv_report(
        self,
        faults: List[Dict],
        metrics: Optional[Dict] = None
    ) -> str:
        """
        Generate a CSV report of faults.
        
        Args:
            faults: List of detected faults
            metrics: Optional metrics to include
            
        Returns:
            CSV formatted string
        """
        if not faults:
            return "No faults detected"
        
        # Ensure faults is a list of dictionaries
        if isinstance(faults, str):
            return faults  # Return the error message
        
        # Create DataFrame from faults
        fault_records = []
        for fault in faults:
            if isinstance(fault, dict):
                record = {
                    'fault_type': fault.get('fault_type', ''),
                    'severity': fault.get('severity', ''),
                    'timestamp': fault.get('timestamp', ''),
                    'description': fault.get('description', ''),
                    'possible_cause': fault.get('possible_cause', ''),
                    'recommended_action': fault.get('recommended_action', ''),
                    'string_id': fault.get('string_id', ''),
                    'value': fault.get('value', ''),
                    'threshold': fault.get('threshold', '')
                }
                fault_records.append(record)
        
        if not fault_records:
            return "No valid fault records"
        
        df = pd.DataFrame(fault_records)
        return df.to_csv(index=False)
    
    def generate_json_report(
        self,
        metrics: Dict[str, Any],
        faults: List[Dict],
        plant_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate a JSON-serializable report.
        
        Args:
            metrics: Efficiency metrics
            faults: Detected faults
            plant_info: Plant information
            
        Returns:
            Dictionary suitable for JSON export
        """
        return {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_type': 'solar_plant_fault_analysis'
            },
            'plant_info': plant_info or {
                'capacity_kw': 500,
                'name': 'Unknown'
            },
            'performance_summary': metrics,
            'fault_summary': {
                'total_faults': len(faults),
                'by_severity': {
                    'critical': sum(1 for f in faults if f.get('severity') == 'critical'),
                    'high': sum(1 for f in faults if f.get('severity') == 'high'),
                    'medium': sum(1 for f in faults if f.get('severity') == 'medium'),
                    'low': sum(1 for f in faults if f.get('severity') == 'low')
                }
            },
            'faults': faults
        }


def generate_report(
    metrics: Dict[str, Any] = None,
    faults: List[Dict] = None,
    plant_info: Optional[Dict] = None,
    format: str = 'text'
) -> Any:
    """
    Convenience function to generate reports.
    
    Args:
        metrics: Efficiency metrics
        faults: Detected faults
        plant_info: Plant information
        format: Output format ('text', 'csv', 'json', 'pdf')
        
    Returns:
        Report in specified format
    """
    generator = ReportGenerator()
    
    # Handle CSV format (only needs faults)
    if format == 'csv':
        # If first argument looks like faults (list), use it directly
        if isinstance(metrics, list):
            return generator.generate_csv_report(metrics, None)
        return generator.generate_csv_report(faults or [], metrics)
    
    # Handle other formats
    if format == 'text':
        return generator.generate_text_report(metrics or {}, faults or [], plant_info)
    elif format == 'json':
        return generator.generate_json_report(metrics or {}, faults or [], plant_info)
    elif format == 'pdf':
        return generator.generate_pdf_report(metrics or {}, faults or [], plant_info)
    else:
        return generator.generate_text_report(metrics or {}, faults or [], plant_info)
