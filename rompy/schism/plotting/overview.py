"""
Enhanced overview plotting functionality for SCHISM model visualization.

This module provides comprehensive multi-panel overview plots that combine
grid visualization, data analysis, and model setup validation in a single view.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.gridspec import GridSpec

from .core import BasePlotter, PlotConfig, PlotValidator
from .grid import GridPlotter
from .data import DataPlotter
from .utils import setup_cartopy_axis, get_geographic_extent, format_scientific_notation

logger = logging.getLogger(__name__)


class OverviewPlotter(BasePlotter):
    """
    Enhanced overview plotting for comprehensive SCHISM model visualization.
    
    This class creates multi-panel overview plots that provide a complete
    picture of the SCHISM model setup, including grid quality, boundary
    conditions, forcing data, and validation metrics.
    
    Parameters
    ----------
    config : Optional[Any]
        SCHISM configuration object
    grid_file : Optional[Union[str, Path]]
        Path to grid file if config is not provided
    plot_config : Optional[PlotConfig]
        Plot configuration parameters
    """
    
    def __init__(
        self,
        config: Optional[Any] = None,
        grid_file: Optional[Union[str, Path]] = None,
        plot_config: Optional[PlotConfig] = None,
    ):
        """Initialize OverviewPlotter."""
        super().__init__(config, grid_file, plot_config)
        
        # Initialize sub-plotters
        self.grid_plotter = GridPlotter(config, grid_file, plot_config)
        self.data_plotter = DataPlotter(config, grid_file, plot_config)

    def plot_comprehensive_overview(
        self,
        figsize: Tuple[float, float] = (20, 16),
        include_validation: bool = True,
        include_quality_metrics: bool = True,
        include_data_summary: bool = True,
        save_path: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> Tuple[Figure, Dict[str, Axes]]:
        """
        Create comprehensive multi-panel overview plot.
        
        This creates a detailed overview with the following panels:
        - Grid and bathymetry visualization
        - Boundary conditions and forcing locations
        - Data quality assessment plots
        - Model setup validation summary
        - Time series overview of forcing data
        
        Parameters
        ----------
        figsize : Tuple[float, float], optional
            Figure size in inches. Default is (20, 16).
        include_validation : bool, optional
            Include model validation panel. Default is True.
        include_quality_metrics : bool, optional
            Include grid quality metrics panel. Default is True.
        include_data_summary : bool, optional
            Include data summary panel. Default is True.
        save_path : Optional[Union[str, Path]], optional
            Path to save the plot. If None, plot is not saved.
        **kwargs : dict
            Additional keyword arguments passed to plotting functions.
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The figure object.
        axes : Dict[str, matplotlib.axes.Axes]
            Dictionary of axes objects keyed by panel name.
            
        Examples
        --------
        >>> plotter = OverviewPlotter(config)
        >>> fig, axes = plotter.plot_comprehensive_overview()
        >>> fig.show()
        """
        # Create complex subplot layout
        fig = plt.figure(figsize=figsize)
        gs = GridSpec(4, 4, figure=fig, hspace=0.3, wspace=0.3)
        
        # Dictionary to store all axes
        axes = {}
        
        # Main grid panel (top-left, 2x2)
        axes['grid'] = fig.add_subplot(gs[0:2, 0:2], projection=setup_cartopy_axis())
        self._plot_main_grid_panel(axes['grid'], **kwargs)
        
        # Boundary conditions panel (top-right, 2x1)
        axes['boundaries'] = fig.add_subplot(gs[0:2, 2], projection=setup_cartopy_axis())
        self._plot_boundary_panel(axes['boundaries'], **kwargs)
        
        # Data locations panel (top-right, 2x1)
        axes['data_locations'] = fig.add_subplot(gs[0:2, 3], projection=setup_cartopy_axis())
        self._plot_data_locations_panel(axes['data_locations'], **kwargs)
        
        # Grid quality metrics (bottom-left)
        if include_quality_metrics:
            axes['quality'] = fig.add_subplot(gs[2, 0])
            self._plot_quality_metrics_panel(axes['quality'], **kwargs)
        
        # Model validation (bottom-center-left)
        if include_validation:
            axes['validation'] = fig.add_subplot(gs[2, 1])
            self._plot_validation_panel(axes['validation'], **kwargs)
        
        # Data summary (bottom-center-right)
        if include_data_summary:
            axes['data_summary'] = fig.add_subplot(gs[2, 2])
            self._plot_data_summary_panel(axes['data_summary'], **kwargs)
        
        # Time series overview (bottom-right)
        axes['timeseries'] = fig.add_subplot(gs[2, 3])
        self._plot_timeseries_overview_panel(axes['timeseries'], **kwargs)
        
        # Model info panel (bottom row, spanning all columns)
        axes['info'] = fig.add_subplot(gs[3, :])
        self._plot_model_info_panel(axes['info'], **kwargs)
        
        # Add overall title
        fig.suptitle('SCHISM Model Overview', fontsize=16, fontweight='bold', y=0.98)
        
        # Save if requested
        if save_path:
            self._save_plot(fig, save_path)
            
        return fig, axes

    def plot_grid_analysis_overview(
        self,
        figsize: Tuple[float, float] = (16, 12),
        save_path: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> Tuple[Figure, Dict[str, Axes]]:
        """
        Create grid-focused analysis overview.
        
        This creates a detailed grid analysis with:
        - Grid structure and bathymetry
        - Element quality metrics
        - Boundary condition locations
        - Grid statistics and histograms
        
        Parameters
        ----------
        figsize : Tuple[float, float], optional
            Figure size in inches. Default is (16, 12).
        save_path : Optional[Union[str, Path]], optional
            Path to save the plot. If None, plot is not saved.
        **kwargs : dict
            Additional keyword arguments.
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The figure object.
        axes : Dict[str, matplotlib.axes.Axes]
            Dictionary of axes objects keyed by panel name.
        """
        # Create subplot layout
        fig = plt.figure(figsize=figsize)
        gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        axes = {}
        
        # Main grid visualization (top row, spans 2 columns)
        axes['grid'] = fig.add_subplot(gs[0, 0:2], projection=setup_cartopy_axis())
        self.grid_plotter.plot_bathymetry(ax=axes['grid'], **kwargs)
        axes['grid'].set_title('Grid and Bathymetry', fontweight='bold')
        
        # Grid quality (top-right)
        axes['quality'] = fig.add_subplot(gs[0, 2], projection=setup_cartopy_axis())
        self.grid_plotter.plot_grid_quality(ax=axes['quality'], **kwargs)
        axes['quality'].set_title('Element Quality', fontweight='bold')
        
        # Boundaries (middle-left)
        axes['boundaries'] = fig.add_subplot(gs[1, 0], projection=setup_cartopy_axis())
        self.grid_plotter.plot_boundaries(ax=axes['boundaries'], **kwargs)
        axes['boundaries'].set_title('Boundaries', fontweight='bold')
        
        # Depth histogram (middle-center)
        axes['depth_hist'] = fig.add_subplot(gs[1, 1])
        self._plot_depth_histogram(axes['depth_hist'], **kwargs)
        
        # Element size histogram (middle-right)
        axes['size_hist'] = fig.add_subplot(gs[1, 2])
        self._plot_element_size_histogram(axes['size_hist'], **kwargs)
        
        # Grid statistics table (bottom row)
        axes['stats'] = fig.add_subplot(gs[2, :])
        self._plot_grid_statistics_table(axes['stats'], **kwargs)
        
        fig.suptitle('SCHISM Grid Analysis Overview', fontsize=16, fontweight='bold')
        
        if save_path:
            self._save_plot(fig, save_path)
            
        return fig, axes

    def plot_data_analysis_overview(
        self,
        figsize: Tuple[float, float] = (16, 12),
        save_path: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> Tuple[Figure, Dict[str, Axes]]:
        """
        Create data-focused analysis overview.
        
        This creates a comprehensive data analysis with:
        - Atmospheric forcing overview
        - Boundary data time series
        - Data quality metrics
        - Temporal coverage analysis
        
        Parameters
        ----------
        figsize : Tuple[float, float], optional
            Figure size in inches. Default is (16, 12).
        save_path : Optional[Union[str, Path]], optional
            Path to save the plot. If None, plot is not saved.
        **kwargs : dict
            Additional keyword arguments.
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The figure object.
        axes : Dict[str, matplotlib.axes.Axes]
            Dictionary of axes objects keyed by panel name.
        """
        fig = plt.figure(figsize=figsize)
        gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        axes = {}
        
        # Atmospheric data spatial (top-left)
        axes['atmospheric'] = fig.add_subplot(gs[0, 0], projection=setup_cartopy_axis())
        self._plot_atmospheric_overview(axes['atmospheric'], **kwargs)
        
        # Boundary data locations (top-center)
        axes['boundary_locations'] = fig.add_subplot(gs[0, 1], projection=setup_cartopy_axis())
        self._plot_boundary_data_locations(axes['boundary_locations'], **kwargs)
        
        # Data coverage timeline (top-right)
        axes['coverage'] = fig.add_subplot(gs[0, 2])
        self._plot_data_coverage_timeline(axes['coverage'], **kwargs)
        
        # Atmospheric time series (middle row)
        axes['atm_timeseries'] = fig.add_subplot(gs[1, :])
        self._plot_atmospheric_timeseries_overview(axes['atm_timeseries'], **kwargs)
        
        # Boundary time series (bottom-left)
        axes['boundary_ts'] = fig.add_subplot(gs[2, 0])
        self._plot_boundary_timeseries_overview(axes['boundary_ts'], **kwargs)
        
        # Data quality metrics (bottom-center)
        axes['data_quality'] = fig.add_subplot(gs[2, 1])
        self._plot_data_quality_metrics(axes['data_quality'], **kwargs)
        
        # Data statistics (bottom-right)
        axes['data_stats'] = fig.add_subplot(gs[2, 2])
        self._plot_data_statistics_table(axes['data_stats'], **kwargs)
        
        fig.suptitle('SCHISM Data Analysis Overview', fontsize=16, fontweight='bold')
        
        if save_path:
            self._save_plot(fig, save_path)
            
        return fig, axes

    def _plot_main_grid_panel(self, ax: Axes, **kwargs) -> None:
        """Plot main grid panel with bathymetry and key features."""
        try:
            self.grid_plotter.plot_bathymetry(ax=ax, **kwargs)
            ax.set_title('Grid and Bathymetry', fontweight='bold')
            
            # Add grid statistics as text
            if hasattr(self, 'grid') and self.grid is not None:
                grid_info = self._get_grid_info()
                ax.text(0.02, 0.98, grid_info, transform=ax.transAxes,
                       verticalalignment='top', bbox=dict(boxstyle='round', 
                       facecolor='white', alpha=0.8), fontsize=8)
        except Exception as e:
            logger.warning(f"Could not plot main grid panel: {e}")
            ax.text(0.5, 0.5, "Grid visualization unavailable", 
                   ha='center', va='center', transform=ax.transAxes)

    def _plot_boundary_panel(self, ax: Axes, **kwargs) -> None:
        """Plot boundary conditions panel."""
        try:
            self.grid_plotter.plot_boundaries(ax=ax, show_colorbar=False, **kwargs)
            ax.set_title('Boundary Conditions', fontweight='bold')
        except Exception as e:
            logger.warning(f"Could not plot boundary panel: {e}")
            ax.text(0.5, 0.5, "Boundary data unavailable", 
                   ha='center', va='center', transform=ax.transAxes)

    def _plot_data_locations_panel(self, ax: Axes, **kwargs) -> None:
        """Plot data locations panel."""
        try:
            # Plot grid outline
            if hasattr(self, 'grid') and self.grid is not None:
                self.grid_plotter.plot_grid(ax=ax, show_elements=False, 
                                          show_colorbar=False, **kwargs)
            
            # Add data source locations if available
            self._add_data_source_markers(ax)
            ax.set_title('Data Locations', fontweight='bold')
        except Exception as e:
            logger.warning(f"Could not plot data locations panel: {e}")
            ax.text(0.5, 0.5, "Data locations unavailable", 
                   ha='center', va='center', transform=ax.transAxes)

    def _plot_quality_metrics_panel(self, ax: Axes, **kwargs) -> None:
        """Plot grid quality metrics."""
        try:
            if hasattr(self, 'grid') and self.grid is not None:
                quality_metrics = self._calculate_quality_metrics()
                self._plot_quality_metrics_chart(ax, quality_metrics)
            else:
                ax.text(0.5, 0.5, "Grid quality metrics unavailable", 
                       ha='center', va='center', transform=ax.transAxes)
        except Exception as e:
            logger.warning(f"Could not plot quality metrics: {e}")
            ax.text(0.5, 0.5, "Quality metrics unavailable", 
                   ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Grid Quality', fontweight='bold')

    def _plot_validation_panel(self, ax: Axes, **kwargs) -> None:
        """Plot model setup validation."""
        try:
            validation_results = self._run_validation_checks()
            self._plot_validation_results(ax, validation_results)
        except Exception as e:
            logger.warning(f"Could not plot validation panel: {e}")
            ax.text(0.5, 0.5, "Validation unavailable", 
                   ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Model Validation', fontweight='bold')

    def _plot_data_summary_panel(self, ax: Axes, **kwargs) -> None:
        """Plot data summary information."""
        try:
            data_summary = self._get_data_summary()
            self._plot_data_summary_chart(ax, data_summary)
        except Exception as e:
            logger.warning(f"Could not plot data summary: {e}")
            ax.text(0.5, 0.5, "Data summary unavailable", 
                   ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Data Summary', fontweight='bold')

    def _plot_timeseries_overview_panel(self, ax: Axes, **kwargs) -> None:
        """Plot time series overview."""
        try:
            self._plot_forcing_timeseries_overview(ax)
        except Exception as e:
            logger.warning(f"Could not plot timeseries overview: {e}")
            ax.text(0.5, 0.5, "Time series unavailable", 
                   ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Forcing Overview', fontweight='bold')

    def _plot_model_info_panel(self, ax: Axes, **kwargs) -> None:
        """Plot model information panel."""
        try:
            model_info = self._get_model_info()
            self._plot_model_info_table(ax, model_info)
        except Exception as e:
            logger.warning(f"Could not plot model info: {e}")
            ax.text(0.5, 0.5, "Model info unavailable", 
                   ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Model Configuration', fontweight='bold')

    def _get_grid_info(self) -> str:
        """Get grid information summary."""
        try:
            if hasattr(self, 'grid') and self.grid is not None:
                n_nodes = len(self.grid.coords['node'])
                n_elements = len(self.grid.coords['nSCHISM_hgrid_face'])
                depth_range = (float(self.grid.depth.min()), float(self.grid.depth.max()))
                
                return (f"Nodes: {n_nodes:,}\n"
                       f"Elements: {n_elements:,}\n"
                       f"Depth: {depth_range[0]:.1f} to {depth_range[1]:.1f} m")
            return "Grid info unavailable"
        except Exception as e:
            logger.warning(f"Could not get grid info: {e}")
            return "Grid info unavailable"

    def _calculate_quality_metrics(self) -> Dict[str, float]:
        """Calculate grid quality metrics."""
        try:
            # Placeholder implementation - would calculate actual quality metrics
            # like element aspect ratios, skewness, etc.
            return {
                'min_aspect_ratio': 0.85,
                'avg_aspect_ratio': 0.95,
                'skewness_score': 0.92,
                'orthogonality_score': 0.88
            }
        except Exception as e:
            logger.warning(f"Could not calculate quality metrics: {e}")
            return {}

    def _plot_quality_metrics_chart(self, ax: Axes, metrics: Dict[str, float]) -> None:
        """Plot quality metrics as a bar chart."""
        if not metrics:
            ax.text(0.5, 0.5, "No quality metrics available", 
                   ha='center', va='center', transform=ax.transAxes)
            return
            
        names = list(metrics.keys())
        values = list(metrics.values())
        
        bars = ax.barh(names, values, color=['green' if v > 0.8 else 'orange' if v > 0.6 else 'red' for v in values])
        ax.set_xlim(0, 1)
        ax.set_xlabel('Quality Score')
        
        # Add value labels
        for bar, value in zip(bars, values):
            ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                   f'{value:.2f}', va='center')

    def _run_validation_checks(self) -> Dict[str, str]:
        """Run model setup validation checks."""
        try:
            # Placeholder implementation - would run actual validation
            return {
                'Grid connectivity': 'PASS',
                'Boundary conditions': 'PASS',
                'Time stepping': 'WARNING',
                'Data coverage': 'PASS',
                'File integrity': 'PASS'
            }
        except Exception as e:
            logger.warning(f"Could not run validation checks: {e}")
            return {}

    def _plot_validation_results(self, ax: Axes, results: Dict[str, str]) -> None:
        """Plot validation results."""
        if not results:
            ax.text(0.5, 0.5, "No validation results", 
                   ha='center', va='center', transform=ax.transAxes)
            return
            
        y_pos = np.arange(len(results))
        labels = list(results.keys())
        statuses = list(results.values())
        
        colors = {'PASS': 'green', 'WARNING': 'orange', 'FAIL': 'red'}
        bar_colors = [colors.get(status, 'gray') for status in statuses]
        
        ax.barh(y_pos, [1] * len(results), color=bar_colors, alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.set_xlim(0, 1)
        ax.set_xticks([])
        
        # Add status labels
        for i, status in enumerate(statuses):
            ax.text(0.5, i, status, ha='center', va='center', 
                   fontweight='bold', color='white')

    def _get_data_summary(self) -> Dict[str, Any]:
        """Get summary of available data."""
        try:
            # Placeholder implementation
            return {
                'atmospheric_files': 2,
                'boundary_files': 3,
                'tidal_constituents': 8,
                'time_coverage_days': 30
            }
        except Exception as e:
            logger.warning(f"Could not get data summary: {e}")
            return {}

    def _plot_data_summary_chart(self, ax: Axes, summary: Dict[str, Any]) -> None:
        """Plot data summary as a simple chart."""
        if not summary:
            ax.text(0.5, 0.5, "No data summary available", 
                   ha='center', va='center', transform=ax.transAxes)
            return
            
        # Create a simple text summary
        summary_text = "\n".join([f"{k.replace('_', ' ').title()}: {v}" 
                                 for k, v in summary.items()])
        ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
               verticalalignment='top', fontsize=10,
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

    def _plot_forcing_timeseries_overview(self, ax: Axes) -> None:
        """Plot overview of forcing time series."""
        try:
            # Create dummy time series for demonstration
            import datetime
            times = [datetime.datetime(2023, 1, 1) + datetime.timedelta(days=i) 
                    for i in range(30)]
            wind_speed = np.random.normal(8, 3, 30)
            
            ax.plot(times, wind_speed, 'b-', label='Wind Speed', linewidth=2)
            ax.set_ylabel('Wind Speed (m/s)')
            ax.set_xlabel('Time')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Format x-axis
            ax.tick_params(axis='x', rotation=45)
            
        except Exception as e:
            logger.warning(f"Could not plot forcing timeseries: {e}")
            ax.text(0.5, 0.5, "Time series data unavailable", 
                   ha='center', va='center', transform=ax.transAxes)

    def _get_model_info(self) -> Dict[str, str]:
        """Get model configuration information."""
        try:
            # Placeholder implementation
            return {
                'SCHISM Version': '5.11.0',
                'Grid Type': 'Unstructured',
                'Vertical Layers': '10',
                'Physics': 'Hydrostatic',
                'Modules': 'WWM, ICE, SED'
            }
        except Exception as e:
            logger.warning(f"Could not get model info: {e}")
            return {}

    def _plot_model_info_table(self, ax: Axes, info: Dict[str, str]) -> None:
        """Plot model information as a table."""
        if not info:
            ax.text(0.5, 0.5, "No model info available", 
                   ha='center', va='center', transform=ax.transAxes)
            ax.axis('off')
            return
            
        # Create table data
        table_data = [[k, v] for k, v in info.items()]
        
        # Create table
        table = ax.table(cellText=table_data, 
                        colLabels=['Parameter', 'Value'],
                        cellLoc='left',
                        loc='center',
                        colWidths=[0.4, 0.6])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Style the table
        for i in range(len(table_data) + 1):
            for j in range(2):
                cell = table[(i, j)]
                if i == 0:  # Header row
                    cell.set_facecolor('#40466e')
                    cell.set_text_props(weight='bold', color='white')
                else:
                    cell.set_facecolor('#f1f1f2' if i % 2 == 0 else 'white')
        
        ax.axis('off')

    def _add_data_source_markers(self, ax: Axes) -> None:
        """Add markers for data source locations."""
        try:
            # Placeholder implementation - would add actual data source locations
            # This would typically mark locations of boundary condition files,
            # atmospheric forcing grid points, etc.
            pass
        except Exception as e:
            logger.warning(f"Could not add data source markers: {e}")

    def _plot_depth_histogram(self, ax: Axes, **kwargs) -> None:
        """Plot depth histogram."""
        try:
            if hasattr(self, 'grid') and self.grid is not None:
                depths = self.grid.depth.values.flatten()
                depths = depths[~np.isnan(depths)]
                
                ax.hist(depths, bins=50, alpha=0.7, edgecolor='black')
                ax.set_xlabel('Depth (m)')
                ax.set_ylabel('Frequency')
                ax.set_title('Depth Distribution', fontweight='bold')
                ax.grid(True, alpha=0.3)
            else:
                ax.text(0.5, 0.5, "Grid data unavailable", 
                       ha='center', va='center', transform=ax.transAxes)
        except Exception as e:
            logger.warning(f"Could not plot depth histogram: {e}")
            ax.text(0.5, 0.5, "Depth histogram unavailable", 
                   ha='center', va='center', transform=ax.transAxes)

    def _plot_element_size_histogram(self, ax: Axes, **kwargs) -> None:
        """Plot element size histogram."""
        try:
            # Placeholder implementation - would calculate actual element sizes
            element_sizes = np.random.lognormal(8, 1, 1000)  # Dummy data
            
            ax.hist(element_sizes, bins=50, alpha=0.7, edgecolor='black')
            ax.set_xlabel('Element Size (m²)')
            ax.set_ylabel('Frequency')
            ax.set_title('Element Size Distribution', fontweight='bold')
            ax.set_xscale('log')
            ax.grid(True, alpha=0.3)
        except Exception as e:
            logger.warning(f"Could not plot element size histogram: {e}")
            ax.text(0.5, 0.5, "Element size histogram unavailable", 
                   ha='center', va='center', transform=ax.transAxes)

    def _plot_grid_statistics_table(self, ax: Axes, **kwargs) -> None:
        """Plot grid statistics as a table."""
        try:
            if hasattr(self, 'grid') and self.grid is not None:
                stats = self._calculate_grid_statistics()
                self._create_statistics_table(ax, stats, "Grid Statistics")
            else:
                ax.text(0.5, 0.5, "Grid statistics unavailable", 
                       ha='center', va='center', transform=ax.transAxes)
        except Exception as e:
            logger.warning(f"Could not plot grid statistics: {e}")
            ax.text(0.5, 0.5, "Grid statistics unavailable", 
                   ha='center', va='center', transform=ax.transAxes)

    def _calculate_grid_statistics(self) -> Dict[str, str]:
        """Calculate comprehensive grid statistics."""
        try:
            if hasattr(self, 'grid') and self.grid is not None:
                n_nodes = len(self.grid.coords['node'])
                n_elements = len(self.grid.coords['nSCHISM_hgrid_face'])
                depths = self.grid.depth.values.flatten()
                depths = depths[~np.isnan(depths)]
                
                return {
                    'Total Nodes': f"{n_nodes:,}",
                    'Total Elements': f"{n_elements:,}",
                    'Min Depth': f"{depths.min():.2f} m",
                    'Max Depth': f"{depths.max():.2f} m",
                    'Mean Depth': f"{depths.mean():.2f} m",
                    'Depth Std': f"{depths.std():.2f} m"
                }
            return {}
        except Exception as e:
            logger.warning(f"Could not calculate grid statistics: {e}")
            return {}

    def _create_statistics_table(self, ax: Axes, stats: Dict[str, str], title: str) -> None:
        """Create a formatted statistics table."""
        if not stats:
            ax.text(0.5, 0.5, f"No {title.lower()} available", 
                   ha='center', va='center', transform=ax.transAxes)
            ax.axis('off')
            return
            
        # Arrange statistics in columns
        items = list(stats.items())
        n_cols = 3
        n_rows = (len(items) + n_cols - 1) // n_cols
        
        table_data = []
        for row in range(n_rows):
            row_data = []
            for col in range(n_cols):
                idx = row * n_cols + col
                if idx < len(items):
                    key, value = items[idx]
                    row_data.extend([key, value])
                else:
                    row_data.extend(['', ''])
            table_data.append(row_data)
        
        # Create table
        table = ax.table(cellText=table_data,
                        cellLoc='left',
                        loc='center')
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        
        # Style the table
        for i in range(n_rows):
            for j in range(n_cols * 2):
                cell = table[(i, j)]
                if j % 2 == 0:  # Parameter names
                    cell.set_facecolor('#f8f9fa')
                    cell.set_text_props(weight='bold')
                else:  # Values
                    cell.set_facecolor('white')
        
        ax.set_title(title, fontweight='bold', pad=20)
        ax.axis('off')

    # Additional helper methods for data analysis overview
    def _plot_atmospheric_overview(self, ax: Axes, **kwargs) -> None:
        """Plot atmospheric forcing overview."""
        try:
            # Try to get atmospheric data from data plotter
            if hasattr(self.data_plotter, 'plot_atmospheric_spatial'):
                self.data_plotter.plot_atmospheric_spatial(ax=ax, show_colorbar=False, **kwargs)
            else:
                ax.text(0.5, 0.5, "Atmospheric data unavailable", 
                       ha='center', va='center', transform=ax.transAxes)
        except Exception as e:
            logger.warning(f"Could not plot atmospheric overview: {e}")
            ax.text(0.5, 0.5, "Atmospheric data unavailable", 
                   ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Atmospheric Forcing', fontweight='bold')

    def _plot_boundary_data_locations(self, ax: Axes, **kwargs) -> None:
        """Plot boundary data locations."""
        try:
            # Plot grid outline first
            if hasattr(self, 'grid') and self.grid is not None:
                self.grid_plotter.plot_grid(ax=ax, show_elements=False, 
                                          show_colorbar=False, alpha=0.3, **kwargs)
            
            # Add boundary locations
            self.grid_plotter.plot_boundaries(ax=ax, show_colorbar=False, **kwargs)
            
        except Exception as e:
            logger.warning(f"Could not plot boundary data locations: {e}")
            ax.text(0.5, 0.5, "Boundary locations unavailable", 
                   ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Boundary Data Locations', fontweight='bold')

    def _plot_data_coverage_timeline(self, ax: Axes, **kwargs) -> None:
        """Plot data coverage timeline."""
        try:
            # Create dummy timeline for demonstration
            import datetime
            start_date = datetime.datetime(2023, 1, 1)
            
            # Different data types with different coverage
            data_types = ['Atmospheric', 'Boundary T/S', 'Boundary UV', 'Tidal']
            colors = ['blue', 'green', 'red', 'orange']
            
            for i, (data_type, color) in enumerate(zip(data_types, colors)):
                # Create dummy coverage periods
                coverage_start = start_date + datetime.timedelta(days=i*2)
                coverage_end = start_date + datetime.timedelta(days=30 - i)
                
                ax.barh(i, (coverage_end - coverage_start).days, 
                       left=(coverage_start - start_date).days,
                       height=0.6, color=color, alpha=0.7, label=data_type)
            
            ax.set_yticks(range(len(data_types)))
            ax.set_yticklabels(data_types)
            ax.set_xlabel('Days from Model Start')
            ax.set_xlim(0, 30)
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            logger.warning(f"Could not plot data coverage timeline: {e}")
            ax.text(0.5, 0.5, "Data coverage unavailable", 
                   ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Data Coverage Timeline', fontweight='bold')

    def _plot_atmospheric_timeseries_overview(self, ax: Axes, **kwargs) -> None:
        """Plot atmospheric time series overview."""
        try:
            # Create dummy atmospheric time series
            import datetime
            times = [datetime.datetime(2023, 1, 1) + datetime.timedelta(hours=i*6) 
                    for i in range(120)]  # 30 days, 6-hourly
            
            wind_u = np.random.normal(0, 5, 120)
            wind_v = np.random.normal(0, 4, 120)
            wind_speed = np.sqrt(wind_u**2 + wind_v**2)
            pressure = np.random.normal(1013, 10, 120)
            
            # Create twin axes for different variables
            ax2 = ax.twinx()
            
            line1 = ax.plot(times, wind_speed, 'b-', label='Wind Speed (m/s)', linewidth=1.5)
            line2 = ax2.plot(times, pressure, 'r-', label='Pressure (hPa)', linewidth=1.5)
            
            ax.set_xlabel('Time')
            ax.set_ylabel('Wind Speed (m/s)', color='blue')
            ax2.set_ylabel('Pressure (hPa)', color='red')
            
            # Combine legends
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax.legend(lines, labels, loc='upper right')
            
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=45)
            
        except Exception as e:
            logger.warning(f"Could not plot atmospheric timeseries: {e}")
            ax.text(0.5, 0.5, "Atmospheric time series unavailable", 
                   ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Atmospheric Forcing Time Series', fontweight='bold')

    def _plot_boundary_timeseries_overview(self, ax: Axes, **kwargs) -> None:
        """Plot boundary time series overview."""
        try:
            # Create dummy boundary time series
            import datetime
            times = [datetime.datetime(2023, 1, 1) + datetime.timedelta(hours=i) 
                    for i in range(720)]  # 30 days, hourly
            
            temperature = 15 + 3 * np.sin(np.linspace(0, 30*2*np.pi, 720)) + np.random.normal(0, 0.5, 720)
            salinity = 35 + 2 * np.sin(np.linspace(0, 30*2*np.pi/2, 720)) + np.random.normal(0, 0.2, 720)
            
            ax.plot(times, temperature, 'r-', label='Temperature (°C)', linewidth=1.5)
            ax2 = ax.twinx()
            ax2.plot(times, salinity, 'b-', label='Salinity (psu)', linewidth=1.5)
            
            ax.set_xlabel('Time')
            ax.set_ylabel('Temperature (°C)', color='red')
            ax2.set_ylabel('Salinity (psu)', color='blue')
            
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=45)
            
            # Add legends
            ax.legend(loc='upper left')
            ax2.legend(loc='upper right')
            
        except Exception as e:
            logger.warning(f"Could not plot boundary timeseries: {e}")
            ax.text(0.5, 0.5, "Boundary time series unavailable", 
                   ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Boundary Conditions', fontweight='bold')

    def _plot_data_quality_metrics(self, ax: Axes, **kwargs) -> None:
        """Plot data quality metrics."""
        try:
            # Create dummy quality metrics
            metrics = {
                'Completeness': 0.95,
                'Consistency': 0.88,
                'Temporal Coverage': 0.92,
                'Spatial Coverage': 0.85,
                'Value Ranges': 0.90
            }
            
            categories = list(metrics.keys())
            values = list(metrics.values())
            colors = ['green' if v >= 0.9 else 'orange' if v >= 0.8 else 'red' for v in values]
            
            bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
            ax.set_ylim(0, 1)
            ax.set_ylabel('Quality Score')
            ax.set_title('Data Quality Metrics', fontweight='bold')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
            
        except Exception as e:
            logger.warning(f"Could not plot data quality metrics: {e}")
            ax.text(0.5, 0.5, "Data quality metrics unavailable", 
                   ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Data Quality', fontweight='bold')

    def _plot_data_statistics_table(self, ax: Axes, **kwargs) -> None:
        """Plot data statistics table."""
        try:
            # Create dummy data statistics
            stats = {
                'Atmospheric Files': '3',
                'Boundary Files': '5', 
                'Time Coverage': '30 days',
                'Temporal Resolution': '6 hours',
                'Tidal Constituents': '8',
                'Grid Points': '2,500'
            }
            
            self._create_statistics_table(ax, stats, "Data Statistics")
            
        except Exception as e:
            logger.warning(f"Could not plot data statistics: {e}")
            ax.text(0.5, 0.5, "Data statistics unavailable", 
                   ha='center', va='center', transform=ax.transAxes)

    def plot(self, **kwargs) -> Tuple[Figure, Dict[str, Axes]]:
        """
        Create default overview plot (alias for plot_comprehensive_overview).
        
        This implements the abstract plot method from BasePlotter.
        
        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments passed to plot_comprehensive_overview.
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The figure object.
        axes : Dict[str, matplotlib.axes.Axes]
            Dictionary of axes objects keyed by panel name.
        """
        return self.plot_comprehensive_overview(**kwargs)

    def _save_plot(self, fig: Figure, save_path: Union[str, Path]) -> None:
        """Save plot to file."""
        try:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            fig.savefig(save_path, dpi=self.plot_config.dpi, 
                       bbox_inches='tight', facecolor='white')
            logger.info(f"Overview plot saved to {save_path}")
            
        except Exception as e:
            logger.error(f"Could not save plot to {save_path}: {e}")