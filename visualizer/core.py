import glob
import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Union, Optional

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class Visualizer:
    # Constants for config keys
    KEY_DIRECTORY = 'directory'
    KEY_COLUMNS = 'columns'
    KEY_GROUPBY = 'groupby'
    KEY_CHART_TYPE = 'chart_type'
    KEY_CHART_LABEL = 'chart_label'

    def __init__(self):
        self.config_data: List[Dict[str, Any]] = []

    def load_config(self, config_path: str) -> None:
        """
        Loads and validates the configuration file.
        
        Args:
            config_path (str): Path to the JSON configuration file.
            
        Raises:
            FileNotFoundError: If the config file does not exist.
            ValueError: If the JSON is invalid or empty.
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found at {config_path}")

        try:
            with path.open('r', encoding='utf-8') as file:
                config = json.load(file)
            
            if not isinstance(config, list):
                 # Handle case where root is a dict (single config) instead of list
                 if isinstance(config, dict):
                     config = [config]
                 else:
                     raise ValueError("Config file must contain a list of configurations.")

            if not config:
                raise ValueError(f"⚠️ Warning: No config data found in {config_path}.")

            self.config_data = config
            logger.info(f"✅ Loaded {len(self.config_data)} configurations from {config_path}")

        except json.JSONDecodeError:
            raise ValueError(f"❌ Error: Failed to decode JSON from {config_path}.")

    def process_all(self) -> None:
        """Main loop to process all loaded configurations."""
        if not self.config_data:
            logger.warning("No configuration data loaded. Call load_config() first.")
            return

        for i, config in enumerate(self.config_data):
            logger.info(f"--- Processing Config Set {i+1} ---")
            self._process_config_entry(config)

    def _process_config_entry(self, config: Dict[str, Any]) -> None:
        """
        Processes a single configuration entry: finds files and generates charts.
        """
        search_pattern = config.get(self.KEY_DIRECTORY)
        if not search_pattern:
            logger.warning("⚠️ Config entry missing 'directory' pattern. Skipping.")
            return

        # usage of glob.glob with recursive=True to handle ** patterns
        files = [Path(p) for p in glob.glob(search_pattern, recursive=True)]
        
        logger.info(f"Found {len(files)} files matching '{search_pattern}'")

        for file_path in files:
            if file_path.is_dir():
                continue
            
            try:
                self._process_single_file(file_path, config)
            except Exception as e:
                logger.error(f"❌ Failed to process {file_path}: {e}", exc_info=True)

    def _process_single_file(self, file_path: Path, config: Dict[str, Any]) -> None:
        """
        Reads a CSV file, aggregates data, and triggers plotting.
        """
        logger.info(f"⏳ Processing {file_path.name}...")
        
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Failed to read CSV {file_path}: {e}")
            return
        
        target_cols = config.get(self.KEY_COLUMNS)
        groupby_input = config.get(self.KEY_GROUPBY)
        chart_type = config.get(self.KEY_CHART_TYPE)
        
        if not target_cols or not groupby_input or not chart_type:
            logger.warning(f"Skipping {file_path.name}: Missing required config keys (columns, groupby, chart_type).")
            return

        # 1. Prepare Data (Handle Columns)
        plot_col_name = "calculated_value" 
        y_label = "Total"

        if isinstance(target_cols, list):
            # Validate columns exist
            available_cols = [c for c in target_cols if c in df.columns]
            if not available_cols:
                logger.warning(f"Skipping {file_path.name}: None of the columns {target_cols} found.")
                return
            
            # Sum columns
            df[plot_col_name] = df[available_cols].sum(axis=1)
            y_label = config.get(self.KEY_CHART_LABEL, ' + '.join(available_cols))
        else:
            if target_cols not in df.columns:
                logger.warning(f"Skipping {file_path.name}: Column '{target_cols}' not found.")
                return
            df[plot_col_name] = df[target_cols]
            y_label = config.get(self.KEY_CHART_LABEL, target_cols)

        # 2. Prepare Data (Handle GroupBy)
        if isinstance(groupby_input, str):
            groupby_input = [groupby_input]

        for group_col in groupby_input:
            if group_col not in df.columns:
                logger.warning(f"⚠️ Column '{group_col}' not found in {file_path.name}, skipping group.")
                continue

            # Group and Sum
            grouped_df = df.groupby(group_col, as_index=False)[plot_col_name].sum()
            
            # 3. Generate Plot
            self._generate_chart(
                df=grouped_df,
                x_col=group_col,
                y_col=plot_col_name,
                chart_type=chart_type,
                output_dir=file_path.parent,
                base_filename=file_path.stem,
                y_label=y_label
            )

    def _generate_chart(self, df: pd.DataFrame, x_col: str, y_col: str, chart_type: str, output_dir: Path, base_filename: str, y_label: str) -> None:
        """
        Generates and saves a matplotlib chart.
        """
        # Create figure and axis using object-oriented API
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x_data = df[x_col]
        y_data = df[y_col]

        # Use a distinct color
        plot_color = '#2ca02c'

        if chart_type == "line":
            ax.plot(x_data, y_data, marker='o', linestyle='-', color=plot_color, label=y_label, linewidth=2)
            # Add data labels
            for x, y in zip(x_data, y_data):
                ax.text(x, y, f'{int(y)}', ha='center', va='bottom', fontsize=9)
        
        elif chart_type == "bar":
            bars = ax.bar(x_data, y_data, color=plot_color, label=y_label, width=0.6)
            # Add data labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom', fontsize=9)
        else:
            logger.error(f"❌ Error: Unknown chart_type '{chart_type}'. Supported: 'line', 'bar'.")
            plt.close(fig)
            return

        # Formatting
        ax.set_title(f"{base_filename} grouped by {x_col}", fontsize=14)
        ax.set_xlabel(x_col, fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()
        
        # Force integer ticks on X axis if possible/appropriate
        try:
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        except Exception:
            pass # Ignore if x-axis is not numeric (e.g. dates or categories)

        output_filename = f"{base_filename}_{x_col}_{chart_type}.png"
        output_path = output_dir / output_filename
        
        try:
            fig.savefig(output_path)
            logger.info(f"✅ Generated chart: {output_path}")
        except Exception as e:
            logger.error(f"❌ Failed to save chart {output_path}: {e}")
        finally:
            plt.close(fig) # Ensure memory is freed
