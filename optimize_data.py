import pandas as pd
import pickle
import os

BASE_DIR = 'api'

def optimize():
    print("Loading original models...")
    df_path = os.path.join(BASE_DIR, 'df.pkl')
    indices_path = os.path.join(BASE_DIR, 'indices.pkl')
    
    if not os.path.exists(df_path) or not os.path.exists(indices_path):
        print("Original files not found!")
        return

    df = pd.read_pickle(df_path)
    indices = pd.read_pickle(indices_path)
    
    # 1. Convert DataFrame to simple list of dicts
    # We only need title for the current logic (in the loop we access df['title'].iloc[i])
    # But wait, looking at api/index.py:
    # movie_title = df['title'].iloc[i]
    # So we just need a list of titles?
    # Let's see if we use other columns.
    # In api/index.py: `movie_title = df['title'].iloc[i]`
    # We don't seem to use overview/genres/etc in the API currently, 
    # except 'title'.
    # However, to be safe and extensible, let's store a list of dicts with 'title'.
    
    print("Converting DataFrame...")
    movies_list = df['title'].tolist()
    # If we need other columns later, we can add them. For now index.py only uses title from df.
    
    with open(os.path.join(BASE_DIR, 'movies_list.pkl'), 'wb') as f:
        pickle.dump(movies_list, f)
    print(f"Saved movies_list.pkl (len: {len(movies_list)})")

    # 2. Convert Indices Series to simple Dict
    print("Converting Indices...")
    # indices is likely a Series where index=Title, value=Index
    if isinstance(indices, pd.Series):
        indices_dict = indices.to_dict()
    else:
        indices_dict = dict(indices)
        
    # Ensure all keys are strings (handle potential mishaps)
    indices_dict = {str(k): int(v) for k, v in indices_dict.items()}

    with open(os.path.join(BASE_DIR, 'indices_dict.pkl'), 'wb') as f:
        pickle.dump(indices_dict, f)
    print(f"Saved indices_dict.pkl (len: {len(indices_dict)})")
    
    print("Optimization complete.")

if __name__ == "__main__":
    optimize()
