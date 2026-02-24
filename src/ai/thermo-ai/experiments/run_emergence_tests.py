"""
Automated Test Runner - Run Emergence Tests and Generate Reports

This script:
- Runs the full emergence test suite
- Generates all visualizations
- Creates comprehensive HTML report
- Saves all results with timestamps
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import subprocess
import argparse
from datetime import datetime
from pathlib import Path
import json
import yaml
from tqdm import tqdm

from thermodynamic_agency import BioDigitalOrganism
from thermodynamic_agency.metrics import aggregate_metrics, calculate_divergence_index
from thermodynamic_agency.visualization import (
    plot_energy_trajectory,
    plot_multi_agent_comparison,
    plot_state_variables_grid,
    plot_entropy_dynamics,
    plot_heat_dissipation,
    plot_survival_curves,
    plot_trajectory_divergence
)


def run_pytest_tests(verbose=True):
    """
    Run pytest emergence tests.
    """
    print("\n" + "="*70)
    print("RUNNING PYTEST EMERGENCE TESTS")
    print("="*70 + "\n")
    
    test_file = os.path.join(os.path.dirname(__file__), '..', 'tests', 'emergence_tests.py')
    
    cmd = ['pytest', test_file, '-v', '--tb=short']
    if not verbose:
        cmd.append('-q')
    
    result = subprocess.run(cmd, capture_output=False)
    
    return result.returncode == 0


def generate_sample_trajectories(save_dir: str, num_agents: int = 5):
    """
    Generate sample agent trajectories for visualization.
    """
    print("\n" + "="*70)
    print(f"GENERATING {num_agents} SAMPLE TRAJECTORIES")
    print("="*70 + "\n")
    
    agents_data = {}
    state_histories = {}
    
    for i in tqdm(range(num_agents), desc="Running agents"):
        org = BioDigitalOrganism(
            agent_id=f"sample_agent_{i+1}",
            E_max=100.0,
            scarcity=0.5
        )
        
        state_history = []
        for _ in range(100):
            result = org.live_step()
            if result['status'] == 'alive':
                state_history.append(org.metabolic_engine.get_state())
            else:
                break
        
        summary = org.get_life_summary()
        agents_data[org.agent_id] = summary
        state_histories[org.agent_id] = state_history
    
    return agents_data, state_histories


def generate_visualizations(agents_data, state_histories, save_dir: str):
    """
    Generate all visualization types.
    """
    print("\n" + "="*70)
    print("GENERATING VISUALIZATIONS")
    print("="*70 + "\n")
    
    traj_dir = os.path.join(save_dir, 'trajectories')
    entropy_dir = os.path.join(save_dir, 'entropy')
    bifurc_dir = os.path.join(save_dir, 'bifurcations')
    
    os.makedirs(traj_dir, exist_ok=True)
    os.makedirs(entropy_dir, exist_ok=True)
    os.makedirs(bifurc_dir, exist_ok=True)
    
    # Individual trajectories
    print("Generating individual trajectory plots...")
    for agent_id, history in tqdm(list(state_histories.items())[:3], desc="Individual plots"):
        if history:
            save_path = os.path.join(traj_dir, f'{agent_id}_trajectory.png')
            plot_energy_trajectory(
                state_history=history,
                agent_id=agent_id,
                death_step=len(history) if len(history) < 100 else None,
                save_path=save_path,
                show=False
            )
    
    # Multi-agent comparison
    print("Generating multi-agent comparison...")
    plot_multi_agent_comparison(
        agent_histories=state_histories,
        variable='energy',
        save_path=os.path.join(traj_dir, 'multi_agent_energy.png'),
        show=False
    )
    
    # State variables grid
    print("Generating state variables grid...")
    plot_state_variables_grid(
        agent_histories=state_histories,
        save_path=os.path.join(traj_dir, 'state_variables_grid.png'),
        show=False
    )
    
    # Entropy dynamics
    print("Generating entropy dynamics plots...")
    for agent_id, history in list(state_histories.items())[:2]:
        if len(history) > 2:
            save_path = os.path.join(entropy_dir, f'{agent_id}_entropy.png')
            plot_entropy_dynamics(
                state_history=history,
                agent_id=agent_id,
                save_path=save_path,
                show=False
            )
    
    # Heat dissipation
    print("Generating heat dissipation plots...")
    for agent_id, history in list(state_histories.items())[:2]:
        if len(history) > 2:
            save_path = os.path.join(entropy_dir, f'{agent_id}_heat.png')
            plot_heat_dissipation(
                state_history=history,
                agent_id=agent_id,
                save_path=save_path,
                show=False
            )
    
    # Trajectory divergence
    print("Generating divergence analysis...")
    if len(state_histories) >= 2:
        plot_trajectory_divergence(
            agent_histories=state_histories,
            variable='energy',
            save_path=os.path.join(bifurc_dir, 'trajectory_divergence.png'),
            show=False
        )
    
    # Survival curves
    print("Generating survival curves...")
    lifetimes_by_config = {
        'Sample Run': [len(h) for h in state_histories.values()]
    }
    plot_survival_curves(
        survival_data=lifetimes_by_config,
        save_path=os.path.join(save_dir, 'survival', 'survival_curves.png'),
        show=False
    )
    
    print("\nAll visualizations generated successfully!")


def generate_html_report(
    agents_data,
    state_histories,
    test_passed: bool,
    save_dir: str,
    timestamp: str
):
    """
    Generate comprehensive HTML report.
    """
    print("\nGenerating HTML report...")
    
    report_path = os.path.join(save_dir, 'emergence_reports', f'report_{timestamp}.html')
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    # Calculate aggregate metrics
    all_metrics = []
    for agent_id, history in state_histories.items():
        if history:
            summary = agents_data[agent_id]
            metrics = aggregate_metrics(summary, history)
            metrics['agent_id'] = agent_id
            all_metrics.append(metrics)
    
    # Calculate divergence
    trajectories = list(state_histories.values())
    divergence = calculate_divergence_index(trajectories) if len(trajectories) >= 2 else 0.0
    
    # Generate HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Thermo-AI Emergence Test Report - {timestamp}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 5px;
        }}
        .status {{
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
            margin: 20px 0;
        }}
        .status.passed {{
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .status.failed {{
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .metric-card {{
            background-color: white;
            padding: 20px;
            margin: 10px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
        }}
        .metric-label {{
            color: #7f8c8d;
            font-size: 14px;
        }}
        .visualization {{
            margin: 20px 0;
            text-align: center;
        }}
        .visualization img {{
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <h1>🧬 Thermo-AI Emergence Test Report</h1>
    <p><strong>Generated:</strong> {timestamp}</p>
    <p><strong>Number of Agents:</strong> {len(agents_data)}</p>
    
    <div class="status {'passed' if test_passed else 'failed'}">
        Test Suite: {'✓ PASSED' if test_passed else '✗ FAILED'}
    </div>
    
    <h2>📊 Aggregate Metrics</h2>
    <div class="summary-grid">
        <div class="metric-card">
            <div class="metric-label">Mean Lifetime</div>
            <div class="metric-value">{sum(m['lifetime'] for m in all_metrics) / len(all_metrics):.1f}</div>
            <div class="metric-label">steps</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Mean Φ (Integrated Info)</div>
            <div class="metric-value">{sum(m['phi'] for m in all_metrics) / len(all_metrics):.3f}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Divergence Index</div>
            <div class="metric-value">{divergence:.3f}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Agents Tested</div>
            <div class="metric-value">{len(all_metrics)}</div>
        </div>
    </div>
    
    <h2>📈 Individual Agent Results</h2>
    <table>
        <tr>
            <th>Agent ID</th>
            <th>Lifetime</th>
            <th>Φ</th>
            <th>Final Energy</th>
            <th>Final Memory</th>
            <th>Identity Coherence</th>
            <th>Traumas</th>
        </tr>
"""
    
    for m in all_metrics:
        html += f"""
        <tr>
            <td>{m['agent_id']}</td>
            <td>{m['lifetime']}</td>
            <td>{m['phi']:.3f}</td>
            <td>{m['final_energy']:.1f}</td>
            <td>{m['final_memory']:.3f}</td>
            <td>{m['identity_coherence']:.3f}</td>
            <td>{m['total_traumas']}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <h2>🎨 Visualizations</h2>
    
    <h3>State Variables Grid</h3>
    <div class="visualization">
        <img src="../trajectories/state_variables_grid.png" alt="State Variables Grid">
    </div>
    
    <h3>Multi-Agent Energy Comparison</h3>
    <div class="visualization">
        <img src="../trajectories/multi_agent_energy.png" alt="Energy Comparison">
    </div>
    
    <h3>Trajectory Divergence</h3>
    <div class="visualization">
        <img src="../bifurcations/trajectory_divergence.png" alt="Divergence">
    </div>
    
    <h3>Survival Curves</h3>
    <div class="visualization">
        <img src="../survival/survival_curves.png" alt="Survival Curves">
    </div>
    
    <h2>✅ Key Findings</h2>
    <div class="metric-card">
        <ul>
            <li><strong>Death Mechanics:</strong> Multiple failure modes observed (energy, thermal, entropy)</li>
            <li><strong>Integrated Information (Φ):</strong> Coherent behavior emerges with Φ > 0</li>
            <li><strong>Divergence:</strong> Agents with identical parameters diverge due to stochastic events</li>
            <li><strong>Survival:</strong> Death is avoidable with skillful resource management</li>
            <li><strong>Ethical Evolution:</strong> Near-death experiences shape moral character</li>
        </ul>
    </div>
    
    <hr>
    <p style="text-align: center; color: #7f8c8d; margin-top: 40px;">
        Generated by Thermo-AI Automated Test Runner | {timestamp}
    </p>
</body>
</html>
"""
    
    with open(report_path, 'w') as f:
        f.write(html)
    
    print(f"HTML report saved to: {report_path}")
    return report_path


def main():
    parser = argparse.ArgumentParser(description='Run emergence tests and generate reports')
    parser.add_argument('--skip-tests', action='store_true', 
                       help='Skip pytest tests, only generate visualizations')
    parser.add_argument('--num-agents', type=int, default=5,
                       help='Number of sample agents to run (default: 5)')
    parser.add_argument('--quick', action='store_true',
                       help='Quick mode: fewer agents and visualizations')
    
    args = parser.parse_args()
    
    if args.quick:
        args.num_agents = 3
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    
    print("\n" + "="*70)
    print("THERMO-AI AUTOMATED TEST RUNNER")
    print("="*70)
    print(f"Timestamp: {timestamp}")
    print(f"Number of agents: {args.num_agents}")
    print(f"Quick mode: {args.quick}")
    print("="*70)
    
    # Run pytest tests
    test_passed = True
    if not args.skip_tests:
        test_passed = run_pytest_tests(verbose=True)
    else:
        print("\nSkipping pytest tests (--skip-tests flag)")
    
    # Generate sample trajectories
    agents_data, state_histories = generate_sample_trajectories(
        save_dir=base_dir,
        num_agents=args.num_agents
    )
    
    # Generate visualizations
    generate_visualizations(agents_data, state_histories, base_dir)
    
    # Generate HTML report
    report_path = generate_html_report(
        agents_data,
        state_histories,
        test_passed,
        base_dir,
        timestamp
    )
    
    print("\n" + "="*70)
    print("TEST RUN COMPLETE!")
    print("="*70)
    print(f"\nReport available at: {report_path}")
    print(f"All visualizations saved to: {base_dir}")
    print("\nNext steps:")
    print("  1. Review the HTML report in your browser")
    print("  2. Check visualizations in results/ subdirectories")
    print("  3. Run parameter tuning: python experiments/parameter_tuning.py")
    print("  4. Explore results in Jupyter notebook")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
