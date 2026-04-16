import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA

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

    def analyze_trends_over_time(self):
        """
        Analyzes daily trends of key performance indicators (KPIs) to show improvement.
        """
        if self.df.empty:
            return pd.DataFrame()

        # Group by date (ignoring time)
        self.df['Date'] = self.df['Timestamp'].dt.date
        
        # Columns to analyze
        cols = {
            'Satisfaction (1-5)': 'mean',
            'Difficulty (1-5)': 'mean',
            'Thinking Time (minutes)': 'mean',
            'Auto Label': 'count'
        }
        
        # Ensure columns exist before grouping
        existing_cols = {k: v for k, v in cols.items() if k in self.df.columns}
        
        daily_trends = self.df.groupby('Date').agg(existing_cols).rename(columns={'Auto Label': 'Interaction Count'})
        
        # Calculate daily GPS distribution
        gps_dist = self.df.groupby(['Date', 'Auto Label']).size().unstack(fill_value=0)
        daily_trends = pd.concat([daily_trends, gps_dist], axis=1)
        
        return daily_trends

    def calculate_scaffolding_efficiency(self):
        """
        Calculates the efficiency of G.P.S scaffolding.
        Measures the average number of G/P steps taken before a successful S step.
        """
        if self.df.empty: return pd.Series()
        
        efficiency = {}
        for student, group in self.df.groupby('Student Hash'):
            steps = group['Auto Label'].tolist()
            s_indices = [i for i, x in enumerate(steps) if x == 'S']
            
            if not s_indices:
                efficiency[student] = np.nan
                continue
            
            # Count G/P steps preceding each S
            gp_counts = []
            last_s_idx = -1
            for s_idx in s_indices:
                # Count G and P between last S and current S
                segment = steps[last_s_idx+1:s_idx]
                gp_count = len([x for x in segment if x in ['G', 'P']])
                gp_counts.append(gp_count)
                last_s_idx = s_idx
            
            efficiency[student] = np.mean(gp_counts) if gp_counts else 0
            
        return pd.Series(efficiency, name='Avg G/P per S')

    def prove_improvement(self):
        """
        Summarizes evidence of improvement for both students and teachers.
        """
        trends = self.analyze_trends_over_time()
        if trends.empty: return "No data available."

        start_satisfaction = trends['Satisfaction (1-5)'].iloc[0]
        end_satisfaction = trends['Satisfaction (1-5)'].iloc[-1]
        sat_change = ((end_satisfaction - start_satisfaction) / start_satisfaction) * 100

        start_diff = trends['Difficulty (1-5)'].iloc[0]
        end_diff = trends['Difficulty (1-5)'].iloc[-1]
        diff_change = ((end_diff - start_diff) / start_diff) * 100

        total_interactions = trends['Interaction Count'].sum()
        
        summary = f"""
# GPS-AIedu Pilot Analysis Summary

### 1. Student Improvement Evidence
- **Satisfaction Trend**: Satisfaction changed from {start_satisfaction:.2f} to {end_satisfaction:.2f} ({sat_change:+.1f}%). 
- **Perceived Difficulty**: Difficulty changed from {start_diff:.2f} to {end_diff:.2f} ({diff_change:+.1f}%). 
- **Learning Independence**: Average G+P steps per Solve (S) is {self.calculate_scaffolding_efficiency().mean():.2f}.

### 2. Teacher Intelligence (Actionable Data)
- **Total Interactions Logged**: {total_interactions} across {len(self.df['Student Hash'].unique())} unique student sessions.
- **Problematic Topics**: {self.df.groupby('Topic')['Difficulty (1-5)'].mean().idxmax()} identified as most difficult for students.
- **At-Risk Students**: {len(self.df[self.df['Satisfaction (1-5)'] <= 2]['Student Hash'].unique())} students flagged with low satisfaction for teacher follow-up.

### 3. Conclusion
The data suggests that the G.P.S. scaffolding approach is **{'improving' if sat_change > 0 else 'stable' if sat_change > -5 else 'needs adjustment'}**. 
        """
        return summary

    def generate_report(self, output_dir='./reports'):
        """
        Runs the full analysis and saves comprehensive plots and summaries.
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
            plt.figure(figsize=(10, 8))
            sns.heatmap(matrix, annot=True, cmap='YlGnBu', fmt='.2f')
            plt.title('GPS Step Transition Matrix (Behavioral Flow)', fontsize=15)
            plt.savefig(f'{output_dir}/markov_matrix.png')
            plt.close()
            
            # 2. Daily Trends Plot
            trends = self.analyze_trends_over_time()
            if not trends.empty:
                plt.figure(figsize=(12, 6))
                sns.lineplot(data=trends[['Satisfaction (1-5)', 'Difficulty (1-5)']], marker='o')
                plt.title('Learning Stability: Satisfaction vs Difficulty Trends', fontsize=15)
                plt.ylabel('Score (1-5)')
                plt.grid(True, alpha=0.3)
                plt.savefig(f'{output_dir}/learning_trends.png')
                plt.close()

            # 3. Clustering
            clusters, centroids = self.perform_clustering()
            if clusters is not None and not clusters.empty:
                clusters.to_csv(f'{output_dir}/student_clusters.csv')
                
                # PCA for better visualization of multi-dimensional clusters
                cluster_cols = [c for c in ['pct_G', 'pct_P', 'pct_S', 'sequence_score', 'Satisfaction (1-5)'] if c in clusters.columns]
                X = clusters[cluster_cols]
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                pca = PCA(n_components=2)
                X_pca = pca.fit_transform(X_scaled)
                clusters['PCA_Dim1'] = X_pca[:, 0]
                clusters['PCA_Dim2'] = X_pca[:, 1]

                plt.figure(figsize=(10, 8))
                sns.scatterplot(data=clusters, x='PCA_Dim1', y='PCA_Dim2', hue='cluster', palette='Set1', s=120, alpha=0.9, edgecolor='white')
                plt.title('Student Segmentation (PCA Factor Analysis)', fontsize=15)
                plt.xlabel('Dominant Learning Factor (PCA1)', fontsize=12)
                plt.ylabel('Secondary Behavior Factor (PCA2)', fontsize=12)
                plt.grid(True, alpha=0.2)
                plt.savefig(f'{output_dir}/student_segmentation_pca.png')
                plt.close()
            
            # 4. Summary Text Report
            summary = self.prove_improvement()
            with open(f'{output_dir}/impact_report.md', 'w', encoding='utf-8') as f:
                f.write(summary)
            
            print(f"Analysis complete. Report saved to {output_dir}")
            return summary
        except Exception as e:
            print(f"Error during report generation: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    import sys
    # Use real pilot data if available, otherwise fallback
    data_path = 'data/processed/GPS_AIedu_Data - QA - Raw Data.csv'
    if os.path.exists(data_path):
        print(f"Running analysis on REAL pilot data: {data_path}")
        analyzer = GPSBehaviorAnalysis(data_path)
        analyzer.generate_report('reports/pilot_week4_analysis')
    else:
        print("Real data not found. Please ensure data/processed/GPS_AIedu_Data - QA - Raw Data.csv exists.")
