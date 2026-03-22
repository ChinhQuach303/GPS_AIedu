import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

class GPSBehaviorAnalysis:
    """
    Advanced Behavior Analysis for GPS-AIedu project.
    Implements Markov Chain transition analysis and K-means clustering of student behavior.
    """
    
    def __init__(self, data_path_or_df):
        if isinstance(data_path_or_df, str):
            try:
                self.df = pd.read_csv(data_path_or_df)
            except Exception as e:
                print(f"Error loading CSV: {e}")
                self.df = pd.DataFrame()
        else:
            self.df = data_path_or_df
        
        if not self.df.empty:
            self.preprocess_data()

    def preprocess_data(self):
        # Handle cases where column names might have extra spaces
        self.df.columns = [c.strip() for c in self.df.columns]
        
        # Ensure required columns exist
        required = ['Student Hash', 'Auto Label', 'Timestamp']
        missing = [c for c in required if c not in self.df.columns]
        if missing:
            print(f"Warning: Missing required columns: {missing}")
            return

        # Ensure timestamp is datetime
        self.df['Timestamp'] = pd.to_datetime(self.df['Timestamp'], errors='coerce')
        self.df = self.df.dropna(subset=['Timestamp'])
        
        # Sort by student and time
        self.df = self.df.sort_values(['Student Hash', 'Timestamp'])
        
        # Filter for GPS steps (handle NaN and ensure caps)
        if 'Auto Label' in self.df.columns:
            self.df['Auto Label'] = self.df['Auto Label'].astype(str).str.upper()
            self.df = self.df[self.df['Auto Label'].isin(['G', 'P', 'S'])]

    def calculate_markov_transitions(self):
        """
        Calculates the probability matrix of transitions between G, P, and S steps.
        """
        states = ['G', 'P', 'S']
        if self.df.empty:
            return pd.DataFrame(0.0, index=states, columns=states)

        transitions = self.df.copy()
        transitions['Next Step'] = transitions.groupby('Student Hash')['Auto Label'].shift(-1)
        
        # Filter valid transitions within the same student session
        valid_transitions = transitions.dropna(subset=['Next Step'])
        
        if valid_transitions.empty:
            return pd.DataFrame(0.0, index=states, columns=states)

        try:
            matrix = pd.crosstab(valid_transitions['Auto Label'], valid_transitions['Next Step'], normalize='index')
        except (ValueError, ZeroDivisionError):
            matrix = pd.DataFrame(0.0, index=self.df['Auto Label'].unique(), columns=valid_transitions['Next Step'].unique())
        
        # Ensure all states are present in the final matrix
        final_matrix = pd.DataFrame(0.0, index=states, columns=states)
        for s1 in states:
            for s2 in states:
                if s1 in matrix.index and s2 in matrix.columns:
                    final_matrix.loc[s1, s2] = matrix.loc[s1, s2]
        
        return final_matrix

    def extract_student_features(self):
        """
        Aggregates per-student metrics for clustering.
        """
        if self.df.empty:
            return pd.DataFrame()

        # Handle numeric columns safely
        s_col = 'Satisfaction (1-5)' if 'Satisfaction (1-5)' in self.df.columns else None
        d_col = 'Difficulty (1-5)' if 'Difficulty (1-5)' in self.df.columns else None
        
        agg_dict = {'Auto Label': 'count'}
        if s_col: agg_dict[s_col] = 'mean'
        if d_col: agg_dict[d_col] = 'mean'

        student_stats = self.df.groupby('Student Hash').agg(agg_dict).rename(columns={'Auto Label': 'total_steps'})

        # Count occurrences of each step
        gps_counts = self.df.groupby(['Student Hash', 'Auto Label']).size().unstack(fill_value=0)
        
        # Calculate percentages
        for col in ['G', 'P', 'S']:
            if col not in gps_counts.columns:
                student_stats[f'pct_{col}'] = 0.0
            else:
                student_stats[f'pct_{col}'] = gps_counts[col] / student_stats['total_steps']
        
        # Path sequence score (how many times they followed G->P, P->S)
        def calc_sequence_score(group):
            steps = group['Auto Label'].tolist()
            if len(steps) < 2: return 0.0
            score = 0
            for i in range(len(steps)-1):
                if (steps[i] == 'G' and steps[i+1] == 'P') or (steps[i] == 'P' and steps[i+1] == 'S'):
                    score += 1
            return score / (len(steps)-1)
            
        student_stats['sequence_score'] = self.df.groupby('Student Hash').apply(calc_sequence_score)
        return student_stats.fillna(0)

    def perform_clustering(self, n_clusters=3):
        """
        Clusters students based on their interaction profiles using K-means.
        """
        features = self.extract_student_features()
        if features.empty or len(features) < n_clusters:
            print("Not enough data for clustering.")
            return features, None
            
        # Select active features for clustering
        cluster_cols = [c for c in ['pct_G', 'pct_P', 'pct_S', 'sequence_score', 'Satisfaction (1-5)'] if c in features.columns]
        X = features[cluster_cols]
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        features['cluster'] = kmeans.fit_predict(X_scaled)
        
        return features, kmeans.cluster_centers_

    def perform_ancova(self, post_test_col='Post_Score', pre_test_col='Pre_Score', group_col='Group'):
        """
        Performs ANCOVA to compare outcomes between groups while controlling for pre-test scores.
        """
        if self.df.empty or post_test_col not in self.df.columns:
            return None
        try:
            from pingouin import ancova
            res = ancova(data=self.df, dv=post_test_col, covar=pre_test_col, between=group_col)
            return res
        except (ImportError, ValueError) as e:
            print(f"ANCOVA failed: {e}")
            return None

    def generate_report(self, output_dir='./reports'):
        """
        Runs the full analysis and saves plots.
        """
        import os
        if self.df.empty:
            print("Dataframe is empty. Cannot generate report.")
            return
            
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        try:
            # 1. Markov Matrix
            matrix = self.calculate_markov_transitions()
            plt.figure(figsize=(8, 6))
            sns.heatmap(matrix, annot=True, cmap='Blues', fmt='.2f')
            plt.title('GPS Step Transition Matrix (Markov Chain)')
            plt.savefig(f'{output_dir}/markov_matrix.png')
            plt.close()
            
            # 2. Clustering
            clusters, centroids = self.perform_clustering()
            if clusters is not None and not clusters.empty:
                clusters.to_csv(f'{output_dir}/student_clusters.csv')
            
            print(f"Analysis complete. Report saved to {output_dir}")
        except Exception as e:
            print(f"Error during report generation: {e}")

if __name__ == "__main__":
    print("GPS Behavior Analysis module loaded. Ready to process Pilot data.")

if __name__ == "__main__":
    # Example usage (needs raw_data.csv)
    # analyzer = GPSBehaviorAnalysis('data/raw_data.csv')
    # analyzer.generate_report()
    print("GPS Behavior Analysis module loaded. Ready to process Pilot data.")
