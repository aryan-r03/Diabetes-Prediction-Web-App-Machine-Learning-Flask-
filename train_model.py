"""
Training Script
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.diabetes_model import DiabetesModel


def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description='Train diabetes prediction model')
    parser.add_argument(
        '--csv',
        type=str,
        default=None,
        help='Path to CSV file with training data'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='diabetes_model.pkl',
        help='Path to save trained model'
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("DIABETES PREDICTION MODEL TRAINING")
    print("=" * 60)
    
    # Initialize model
    model = DiabetesModel()
    
    # Load dataset
    if args.csv and os.path.exists(args.csv):
        print(f"\nUsing dataset from: {args.csv}")
        df = model.load_dataset_from_csv(args.csv)
    else:
        print("\nNo CSV provided or file not found.")
        print("Creating sample dataset for demonstration...")
        df = model.create_sample_dataset()
    
    # Train model
    accuracy = model.train(df)
    
    # Save model
    model.save_model(args.output)
    
    print("\n" + "-" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"✓ Model accuracy: {accuracy * 100:.2f}%")
    print(f"✓ Model saved to: {args.output}")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
