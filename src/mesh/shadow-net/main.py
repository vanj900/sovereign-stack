"""
Bio-Digital Organism - Main Entry Point
Run the thermodynamic intelligence simulation
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.bio_digital_organism import BioDigitalOrganism


def main():
    """Main entry point for Bio-Digital Organism"""
    parser = argparse.ArgumentParser(
        description="Bio-Digital Organism - A Thermodynamic Intelligence System"
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=100,
        help="Maximum number of cycles to run (default: 100)"
    )
    parser.add_argument(
        "--energy",
        type=float,
        default=100.0,
        help="Initial energy level (default: 100.0)"
    )
    parser.add_argument(
        "--env-size",
        type=int,
        default=10,
        help="Environment grid size (default: 10)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./narratives",
        help="Directory to save narratives (default: ./narratives)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("BIO-DIGITAL ORGANISM")
    print("A Thermodynamic Intelligence System")
    print("=" * 60)
    print()
    print("This is not a chatbot or standard AI agent.")
    print("It is a system that:")
    print("  • Obeys the laws of thermodynamics")
    print("  • Dies by default via entropy")
    print("  • Must make difficult choices under limitation")
    print("  • Forges a 'soul' through suffering, scarcity, and persistence")
    print()
    print("=" * 60)
    print()
    
    # Create and run organism
    organism = BioDigitalOrganism(
        initial_energy=args.energy,
        environment_size=args.env_size,
        output_dir=args.output_dir
    )
    
    # Run simulation
    organism.run_simulation(max_cycles=args.cycles, auto_save=True)
    
    print()
    print("=" * 60)
    print("Simulation complete. Check the narratives directory for the")
    print("organism's life story - a unique record of its struggle against entropy.")
    print("=" * 60)


if __name__ == "__main__":
    main()
