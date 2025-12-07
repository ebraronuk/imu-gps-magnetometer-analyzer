"""Entry point CLI for the IMU-GPS-Magnetometer Analyzer."""
import argparse
from pathlib import Path

from src.pipeline.pipeline import AnalysisArtifacts, PipelineConfig, run_basic_pipeline
from src.visualization.plot_timeseries import plot_timeseries
from src.reporting.report_generator import build_basic_report
from src.simulation.mag_simulator import generate_simulated_rotation


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for basic analysis workflow."""
    parser = argparse.ArgumentParser(
        description="Sensor Log Analyzer for IMU, GPS, Magnetometer, Baro logs"
    )
    parser.add_argument("--input", type=Path, required=False, help="Input CSV log file.")
    parser.add_argument("--time-column", type=str, default="timestamp", help="Time column name.")
    parser.add_argument(
        "--resample-rate",
        type=str,
        default="10ms",
        help="Resampling interval for time synchronization (e.g., '10ms').",
    )
    parser.add_argument(
        "--simulate-mag",
        action="store_true",
        help="Generate synthetic magnetometer/IMU dataset before running analysis.",
    )
    parser.add_argument(
        "--simulate-path",
        type=Path,
        default=Path("example_logs/simulated_rotation.csv"),
        help="Output path for synthetic dataset when using --simulate-mag.",
    )
    parser.add_argument(
        "--no-normalize",
        action="store_true",
        help="Disable z-score normalization on numeric columns.",
    )
    parser.add_argument(
        "--summary", action="store_true", help="Print dataset summary (head, info, stats)."
    )
    parser.add_argument("--fft", action="store_true", help="Compute FFT on numeric signals.")
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Render interactive plots (timeseries and optionally FFT).",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="PyQt5 arayüzünü başlat ve CLI akışını atla.",
    )
    parser.add_argument(
        "--heading",
        action="store_true",
        help="Compute and display tilt-compensated and fused headings.",
    )
    parser.add_argument(
        "--mag-calib",
        action="store_true",
        help="Compute and display magnetometer ellipsoid calibration parameters.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional output HTML report path (basic template).",
    )
    return parser.parse_args()


def main() -> None:
    """Main CLI orchestrating load, preprocess, visualize, and report."""
    args = parse_args()

    if args.gui:
        from src.gui.app import run_gui

        run_gui()
        return

    if args.simulate_mag:
        sim_path = args.simulate_path if args.simulate_path else args.input
        generate_simulated_rotation(sim_path)
        print(f"Synthetic dataset generated at {sim_path}")
        args.input = sim_path
    elif args.input is None:
        raise SystemExit("Input path is required unless --simulate-mag or --gui is used.")

    config = PipelineConfig(
        input_path=args.input,
        time_column=args.time_column,
        resample_rate=args.resample_rate,
        normalize=not args.no_normalize,
        compute_fft=args.fft,
    )

    artifacts: AnalysisArtifacts = run_basic_pipeline(config)

    if args.summary:
        print("Dataset summary:")
        print(artifacts.synced_main_df.head())
        print(artifacts.synced_main_df.describe())

    if args.plot:
        plot_timeseries(artifacts.synced_main_df, time_column=args.time_column, show=True)
        if args.fft and artifacts.fft_figure is not None:
            artifacts.fft_figure.show()

        if args.heading and artifacts.fused_heading is not None:
            heading_df = artifacts.synced_main_df[[args.time_column]].copy()
            fused_heading_aligned = artifacts.fused_heading.reindex(heading_df.index).ffill().bfill()
            heading_df["fused_heading_deg"] = fused_heading_aligned.values
            plot_timeseries(heading_df, time_column=args.time_column, value_columns=["fused_heading_deg"], show=True)

    if args.heading:
        if artifacts.mag_heading is not None:
            print("Magnetic heading (tilt-compensated) preview:")
            print(artifacts.mag_heading.head())
        else:
            print("Magnetic heading not available (required mag_x/mag_y/mag_z + accel axes).")
        if artifacts.fused_heading is not None:
            print("Fused heading (complementary) preview:")
            print(artifacts.fused_heading.head())
        else:
            print("Fused heading not available (requires gyro_z and magnetic heading).")

    if args.mag_calib:
        if artifacts.mag_center is not None and artifacts.mag_transform_matrix is not None:
            print("Magnetometer ellipsoid calibration parameters:")
            print(f"Hard-iron center: {artifacts.mag_center}")
            print(f"Soft-iron transform matrix:\n{artifacts.mag_transform_matrix}")
            if artifacts.mag_corrected_df is not None and all(
                col in artifacts.mag_corrected_df.columns for col in ["mag_x", "mag_y", "mag_z"]
            ):
                print("Corrected magnetometer data preview:")
                print(artifacts.mag_corrected_df[["mag_x", "mag_y", "mag_z"]].head())
        else:
            print("Magnetometer calibration not available (missing mag_x/mag_y/mag_z).")

    if args.report:
        html = build_basic_report(
            raw=artifacts.synced_main_df,
            normalized=artifacts.normalized_df,
            fft_fig=artifacts.fft_figure,
            time_column=args.time_column,
        )
        args.report.write_text(html, encoding="utf-8")
        print(f"Report written to {args.report}")

    print("Analysis complete.")


if __name__ == "__main__":
    main()
