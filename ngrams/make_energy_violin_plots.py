import pandas as pd
import os
import torch
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

def load_and_process_file(file_path):
    """Load a PyTorch file and return its mean value."""
    return torch.load(file_path, map_location=torch.device('cpu')).mean().item()

def main():
    data_path = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/Music-Source-Separation-Training/energy/indictts'
    output_path = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngram/scripts/energy_distribution/energy_indictts.csv'
    
    # Get list of .pt files
    files = [f for f in os.listdir(data_path) if f.endswith('.pt')]
    file_paths = [os.path.join(data_path, f) for f in files]
    
    # Use ProcessPoolExecutor for parallel file loading
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(tqdm(executor.map(load_and_process_file, file_paths), total=len(file_paths)))
    
    # Save results to CSV
    pd.DataFrame(results).to_csv(output_path, header=None, index=False)

if __name__ == "__main__":
    main()
