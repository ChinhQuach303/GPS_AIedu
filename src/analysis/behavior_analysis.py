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
        
        # Final cleanup for clustering
        final_features = student_stats.replace([np.inf, -np.inf], 0).fillna(0)
        
        # New: Independence Index (Current snapshot)
        if 'G' in gps_counts.columns and 'P' in gps_counts.columns and 'S' in gps_counts.columns:
            final_features['independence_index'] = gps_counts['S'] / (gps_counts['G'] + gps_counts['P'] + 0.1)
        else:
            final_features['independence_index'] = 0.0
            
        return final_features

    def calculate_learning_gain(self, pre_post_df):
        """
        Calculates normalized learning gain (Hake's g) and Cohen's d effect size.
        Expects a DataFrame with ['Pre_Score', 'Post_Score', 'Group']
        """
        if pre_post_df.empty:
            return pd.DataFrame(), {}
            
        merged = pre_post_df.copy()
        max_score = 100 
        
        # Hake's g: (Post - Pre) / (Max - Pre)
        merged['norm_gain'] = (merged['Post_Score'] - merged['Pre_Score']) / (max_score - merged['Pre_Score'].replace(max_score, max_score-0.1))
        
        # Statistics per group
        stats = {}
        for group, data in merged.groupby('Group'):
            stats[group] = {
                'avg_pre': data['Pre_Score'].mean(),
                'avg_post': data['Post_Score'].mean(),
                'avg_gain': data['norm_gain'].mean(),
                'count': len(data)
            }
            
        # Cohen's d (if we have Experimental and Control)
        if 'Experimental' in stats and 'Control' in stats:
            exp = merged[merged['Group'] == 'Experimental']['Post_Score']
            ctrl = merged[merged['Group'] == 'Control']['Post_Score']
            
            n1, n2 = len(exp), len(ctrl)
            var1, var2 = exp.var(), ctrl.var()
            pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
            
            if pooled_std != 0:
                stats['cohen_d'] = (exp.mean() - ctrl.mean()) / pooled_std
            else:
                stats['cohen_d'] = 0.0
                
        return merged, stats

    def generate_pre_post_template(self, output_path='data/processed/pre_post_comparison_template.csv'):
        """
        Generates a template for teacher to fill in Pre and Post scores.
        """
        students = self.df['Student Hash'].unique()
        template = pd.DataFrame({
            'Student Hash': students,
            'Pre_Score': 0.0,
            'Post_Score': 0.0,
            'Group': 'Experimental'
        })
        # Add some mock control students for structure
        control_mock = pd.DataFrame([
            {'Student Hash': f'control_{i}', 'Pre_Score': 0.0, 'Post_Score': 0.0, 'Group': 'Control'}
            for i in range(5)
        ])
        template = pd.concat([template, control_mock], ignore_index=True)
        template.to_csv(output_path, index=False)
        print(f"Template created at {output_path}")
        return template

    def perform_clustering(self, n_clusters=3):
        """
        Clusters students based on their interaction profiles using K-means.
        """
        features = self.extract_student_features()
        if features.empty or len(features) < n_clusters:
            print("Not enough data for clustering.")
            return features, None
            
        # Select active features for clustering
        cluster_cols = [c for c in ['pct_G', 'pct_P', 'pct_S', 'sequence_score', 'efficiency_score', 'Satisfaction (1-5)'] if c in features.columns]
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
        daily_trends = pd.concat([daily_trends, gps_dist], axis=1).fillna(0)
        
        return daily_trends

    def calculate_sequence_chaos(self):
        """
        Calculates Sequence Chaos Index: entropy-like measure of transitions.
        Pure GPS (G -> P -> S) has low chaos.
        Random jumping (G -> S -> G -> G) has high chaos.
        """
        chaos_scores = {}
        for student, group in self.df.groupby('Student Hash'):
            steps = group['Auto Label'].tolist()
            if len(steps) < 2:
                chaos_scores[student] = 1.0 # Max chaos for low data
                continue
            
            # Count repeated steps or backward jumps
            anomalies = 0
            for i in range(len(steps)-1):
                # Penalty for S -> G or S -> P (Regression after solving)
                if steps[i] == 'S' and steps[i+1] in ['G', 'P']:
                    anomalies += 1.5
                # Penalty for G -> S (Skipping Practice)
                elif steps[i] == 'G' and steps[i+1] == 'S':
                    anomalies += 1.0
                # Penalty for too many repeats of G
                elif steps[i] == 'G' and steps[i+1] == 'G':
                   anomalies += 0.2
            
            chaos_scores[student] = anomalies / len(steps)
            
        return pd.Series(chaos_scores, name='chaos_index')

    def track_cluster_transitions(self, split_date=None):
        """
        Compares clusters before and after a split date to track 'graduation'.
        """
        if self.df.empty: return pd.DataFrame()
        
        if split_date is None:
            # Default to splitting mid-way in time
            dates = sorted(self.df['Timestamp'].dt.date.unique())
            if len(dates) < 2: return pd.DataFrame()
            split_date = dates[len(dates)//2]
            
        df_early = self.df[self.df['Timestamp'].dt.date < split_date]
        df_late = self.df[self.df['Timestamp'].dt.date >= split_date]
        
        if df_early.empty or df_late.empty: return pd.DataFrame()
        
        # Analyze clusters for both periods
        early_analyzer = GPSBehaviorAnalysis(df_early)
        late_analyzer = GPSBehaviorAnalysis(df_late)
        
        early_clusters, _ = early_analyzer.perform_clustering()
        late_clusters, _ = late_analyzer.perform_clustering()
        
        if early_clusters.empty or late_clusters.empty: return pd.DataFrame()
        
        # Merge to see transitions
        transitions = pd.merge(
            early_clusters[['cluster']].rename(columns={'cluster': 'cluster_before'}),
            late_clusters[['cluster']].rename(columns={'cluster': 'cluster_after'}),
            on='Student Hash',
            how='inner'
        )
        
        return transitions

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
                segment = steps[last_s_idx+1:s_idx]
                gp_count = len([x for x in segment if x in ['G', 'P']])
                gp_counts.append(gp_count)
                last_s_idx = s_idx
            
            efficiency[student] = np.mean(gp_counts) if gp_counts else 0
            
        return pd.Series(efficiency, name='Avg G/P per S')

    def calculate_independence_index(self):
        """
        Calculates the Independence Index: Count(S) / (Count(G) + Count(P) + 1).
        A higher index indicates more independence from AI scaffolding.
        Tracks how this index changes over time (Day-by-Day).
        """
        if self.df.empty: return pd.DataFrame()
        
        # Calculate daily counts per student
        self.df['Date'] = self.df['Timestamp'].dt.date
        daily_gps = self.df.groupby(['Date', 'Student Hash', 'Auto Label']).size().unstack(fill_value=0)
        
        # Ensure G, P, S columns exist
        for col in ['G', 'P', 'S']:
            if col not in daily_gps.columns:
                daily_gps[col] = 0
        
        daily_gps['independence_index'] = daily_gps['S'] / (daily_gps['G'] + daily_gps['P'] + 0.1)
        
        # Average across all students per day
        daily_avg_independence = daily_gps.groupby('Date')['independence_index'].mean()
        return daily_avg_independence

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
- **Independence Index (Week 5 Focus)**: Current avg index is {self.calculate_independence_index().iloc[-1]:.2f} (Target: > 1.0).
- **Sequence Chaos (Ordering)**: Avg Chaos Index is {self.calculate_sequence_chaos().mean():.3f} (Lower is better, indicates structured learning).

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
                
            # 4. Chaos Index Distribution
            chaos_scores = self.calculate_sequence_chaos()
            plt.figure(figsize=(10, 6))
            sns.histplot(chaos_scores, kde=True, color='purple')
            plt.title('Sequence Chaos Distribution (Behavioral Consistency)', fontsize=15)
            plt.xlabel('Chaos Index (Lower = More Disciplined)', fontsize=12)
            plt.savefig(f'{output_dir}/chaos_distribution.png')
            plt.close()

            # 5. Graduation / Transitions
            transitions = self.track_cluster_transitions()
            if not transitions.empty:
                transition_matrix = pd.crosstab(transitions['cluster_before'], transitions['cluster_after'], normalize='index')
                plt.figure(figsize=(10, 8))
                sns.heatmap(transition_matrix, annot=True, cmap='RdYlGn', fmt='.2f')
                plt.title('Student Migration: Profile Transitions (Graduation)', fontsize=15)
                plt.xlabel('Late Session Profile (After)', fontsize=12)
                plt.ylabel('Early Session Profile (Before)', fontsize=12)
                plt.savefig(f'{output_dir}/graduation_matrix.png')
                plt.close()
            
            # 6. Independence Index Trend
            independence_trend = self.calculate_independence_index()
            if not independence_trend.empty:
                plt.figure(figsize=(12, 6))
                independence_trend.plot(marker='s', color='green', linewidth=2)
                plt.title('Daily Independence Index (AI Dependency Reduction)', fontsize=15)
                plt.ylabel('Independence Index (S / (G+P+0.1))')
                plt.axhline(y=1.0, color='r', linestyle='--', label='Independence Threshold')
                plt.legend()
                plt.grid(True, alpha=0.3)
                plt.savefig(f'{output_dir}/independence_trend.png')
                plt.close()

            # 7. GPS Step Distribution over Time
            trends = self.analyze_trends_over_time()
            if not trends.empty and all(col in trends.columns for col in ['G', 'P', 'S']):
                plt.figure(figsize=(12, 6))
                trends[['G', 'P', 'S']].plot(kind='bar', stacked=True, color=['#ff9999','#66b3ff','#99ff99'])
                plt.title('Daily GPS Activity Composition', fontsize=15)
                plt.ylabel('Step Count')
                plt.xticks(rotation=45)
                plt.savefig(f'{output_dir}/gps_distribution_bar.png')
                plt.close()

            # 8. Thinking Time vs Difficulty Correlation
            if 'Difficulty (1-5)' in self.df.columns and 'Thinking Time (minutes)' in self.df.columns:
                plt.figure(figsize=(10, 6))
                sns.regplot(data=self.df, x='Difficulty (1-5)', y='Thinking Time (minutes)', scatter_kws={'alpha':0.5})
                plt.title('Cognitive Load: Thinking Time vs complexity', fontsize=15)
                plt.savefig(f'{output_dir}/difficulty_vs_time.png')
                plt.close()
            
            # 9. Pre/Post Comparison (if score data exists)
            score_path = 'data/processed/mock_final_scores.csv'
            if os.path.exists(score_path):
                scores_df = pd.read_csv(score_path)
                final_df, stats = self.calculate_learning_gain(scores_df)
                
                # Plot 1: Pre vs Post Mean Comparison
                plt.figure(figsize=(10, 6))
                comparison_data = final_df.groupby('Group')[['Pre_Score', 'Post_Score']].mean()
                comparison_data.plot(kind='bar', color=['#34495e', '#3498db'])
                plt.title('Comparison of Pre-test vs Post-test Scores', fontsize=15)
                plt.ylabel('Average Score')
                plt.xticks(rotation=0)
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                plt.savefig(f'{output_dir}/pre_post_comparison.png')
                plt.close()
                
                # Plot 2: Normalized Gain Distribution
                plt.figure(figsize=(10, 6))
                sns.boxplot(data=final_df, x='Group', y='norm_gain', palette='Set2')
                plt.title("Distribution of Normalized Learning Gain (Hake's g)", fontsize=15)
                plt.ylabel('Normalized Gain')
                plt.savefig(f'{output_dir}/learning_gain_distribution.png')
                plt.close()
                
                # Save stats to report
                with open(f'{output_dir}/statistical_summary.md', 'w') as f:
                    f.write(f"# Statistical Benchmarking Summary\n\n")
                    f.write(f"- **Cohen's d (Effect Size)**: {stats.get('cohen_d', 0):.3f}\n")
                    for group, s in stats.items():
                        if isinstance(s, dict):
                            f.write(f"### Group: {group}\n")
                            f.write(f"- Avg Pre: {s['avg_pre']:.2f}\n")
                            f.write(f"- Avg Post: {s['avg_post']:.2f}\n")
                            f.write(f"- Avg Normalized Gain: {s['avg_gain']:.2f}\n\n")

            # 10. Summary Text Report
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
