"""
Cross-Dataset Correlation Engine
Identifies relationships between biometric failures, demographic gaps, 
enrolment velocity, and geographic patterns
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class CorrelationEngine:
    """
    Advanced correlation analysis across all three Aadhar datasets.
    """
    
    def __init__(self, biometric_df, demographic_df, enrolment_df):
        """
        Initialize with all three datasets.
        
        Args:
            biometric_df: Biometric authentication DataFrame
            demographic_df: Demographic DataFrame with auth metrics
            enrolment_df: Enrolment DataFrame
        """
        self.biometric_df = biometric_df
        self.demographic_df = demographic_df
        self.enrolment_df = enrolment_df
        
    def create_state_level_features(self):
        """
        Aggregate all datasets to state level for correlation analysis.
        
        Returns:
            pd.DataFrame with state-level features from all datasets
        """
        # Biometric features
        bio_features = self.biometric_df.groupby('state').agg({
            'total_transactions': 'sum',
            'bio_age_5_17': 'sum',
            'bio_age_17_': 'sum',
            'date': 'count'  # Number of days with data
        }).rename(columns={
            'total_transactions': 'bio_total_volume',
            'bio_age_5_17': 'bio_youth_volume',
            'bio_age_17_': 'bio_adult_volume',
            'date': 'bio_data_days'
        })
        
        # Calculate biometric metrics
        bio_features['bio_youth_ratio'] = (bio_features['bio_youth_volume'] / 
                                           bio_features['bio_total_volume'] * 100)
        bio_features['bio_daily_avg'] = bio_features['bio_total_volume'] / bio_features['bio_data_days']
        
        # Calculate volatility (coefficient of variation)
        bio_volatility = self.biometric_df.groupby(['state', 'date'])['total_transactions'].sum()\
            .groupby('state').agg(['mean', 'std'])
        bio_features['bio_volatility'] = (bio_volatility['std'] / bio_volatility['mean'] * 100)
        
        # Demographic features
        demo_features = self.demographic_df.groupby('state').agg({
            'total_demographic': 'sum',
            'auth_status': lambda x: (x == 'Success').sum() / len(x) * 100,
            'response_time_ms': ['median', lambda x: x.quantile(0.95), lambda x: x.quantile(0.99)],
            'demo_age_5_17': 'sum',
            'demo_age_17_': 'sum'
        })
        
        demo_features.columns = [
            'demo_total_volume',
            'demo_success_rate',
            'demo_median_latency',
            'demo_p95_latency',
            'demo_p99_latency',
            'demo_youth_volume',
            'demo_adult_volume'
        ]
        
        demo_features['demo_youth_ratio'] = (demo_features['demo_youth_volume'] / 
                                             demo_features['demo_total_volume'] * 100)
        demo_features['demo_failure_rate'] = 100 - demo_features['demo_success_rate']
        
        # Calculate auth modality diversity (entropy)
        modality_diversity = self.demographic_df.groupby('state')['auth_modality'].apply(
            lambda x: -sum((x.value_counts(normalize=True) * 
                           np.log(x.value_counts(normalize=True))).fillna(0))
        )
        demo_features['demo_modality_diversity'] = modality_diversity
        
        # Error rate by type
        errors = self.demographic_df[self.demographic_df['auth_status'] == 'Failure']
        error_300_rate = errors.groupby('state')['error_code'].apply(
            lambda x: (x == 300).sum() / len(x) * 100 if len(x) > 0 else 0
        )
        demo_features['demo_biometric_error_rate'] = error_300_rate
        
        # Enrolment features
        enrol_features = self.enrolment_df.groupby('state').agg({
            'total_enrolment': 'sum',
            'age_0_5': 'sum',
            'age_5_17': 'sum',
            'age_18_greater': 'sum',
            'date': 'count'
        }).rename(columns={
            'total_enrolment': 'enrol_total_volume',
            'age_0_5': 'enrol_infant_volume',
            'age_5_17': 'enrol_youth_volume',
            'age_18_greater': 'enrol_adult_volume',
            'date': 'enrol_data_days'
        })
        
        enrol_features['enrol_infant_ratio'] = (enrol_features['enrol_infant_volume'] / 
                                                enrol_features['enrol_total_volume'] * 100)
        enrol_features['enrol_daily_avg'] = (enrol_features['enrol_total_volume'] / 
                                             enrol_features['enrol_data_days'])
        
        # Calculate enrolment growth rate (compare first and last month)
        enrol_growth = self.enrolment_df.groupby(['state', 
                                                  self.enrolment_df['date'].dt.to_period('M')])['total_enrolment'].sum()
        
        def calc_growth(group):
            if len(group) < 2:
                return 0
            first_month = group.iloc[0]
            last_month = group.iloc[-1]
            if first_month > 0:
                return (last_month - first_month) / first_month * 100
            return 0
        
        enrol_features['enrol_growth_rate'] = enrol_growth.groupby('state').apply(calc_growth)
        
        # Merge all features
        integrated = bio_features.merge(demo_features, left_index=True, right_index=True, how='outer')
        integrated = integrated.merge(enrol_features, left_index=True, right_index=True, how='outer')
        
        # Fill NaN with 0
        integrated = integrated.fillna(0)
        
        return integrated
    
    def calculate_correlation_matrix(self, method='pearson'):
        """
        Calculate correlation matrix for all state-level features.
        
        Args:
            method: 'pearson', 'spearman', or 'kendall'
            
        Returns:
            pd.DataFrame: Correlation matrix
        """
        state_features = self.create_state_level_features()
        
        # Select numeric columns
        numeric_cols = state_features.select_dtypes(include=[np.number]).columns
        
        if method == 'pearson':
            corr_matrix = state_features[numeric_cols].corr(method='pearson')
        elif method == 'spearman':
            corr_matrix = state_features[numeric_cols].corr(method='spearman')
        elif method == 'kendall':
            corr_matrix = state_features[numeric_cols].corr(method='kendall')
        else:
            raise ValueError("Method must be 'pearson', 'spearman', or 'kendall'")
        
        return corr_matrix
    
    def identify_strong_correlations(self, threshold=0.7, method='pearson'):
        """
        Identify pairs of variables with strong correlations.
        
        Args:
            threshold: Minimum absolute correlation to report
            method: Correlation method
            
        Returns:
            pd.DataFrame with strong correlations
        """
        corr_matrix = self.calculate_correlation_matrix(method=method)
        
        # Extract upper triangle (avoid duplicates)
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
        
        strong_corr = []
        for i in range(len(corr_matrix)):
            for j in range(i+1, len(corr_matrix)):
                if mask[i, j]:
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) >= threshold:
                        strong_corr.append({
                            'Variable 1': corr_matrix.index[i],
                            'Variable 2': corr_matrix.columns[j],
                            'Correlation': corr_val,
                            'Strength': 'Strong Positive' if corr_val >= threshold 
                                       else 'Strong Negative',
                            'Abs_Correlation': abs(corr_val)
                        })
        
        df_corr = pd.DataFrame(strong_corr)
        if len(df_corr) > 0:
            df_corr = df_corr.sort_values('Abs_Correlation', ascending=False)
        
        return df_corr
    
    def analyze_failure_demographic_relationship(self):
        """
        Analyze relationship between biometric failures and demographic gaps.
        
        Returns:
            dict: Analysis results with insights
        """
        state_features = self.create_state_level_features()
        
        # Focus on failure rate vs demographic metrics
        analysis = {
            'correlation_failure_youth': stats.pearsonr(
                state_features['demo_failure_rate'],
                state_features['demo_youth_ratio']
            )[0] if len(state_features) > 2 else 0,
            
            'correlation_failure_latency': stats.pearsonr(
                state_features['demo_failure_rate'],
                state_features['demo_p99_latency']
            )[0] if len(state_features) > 2 else 0,
            
            'correlation_failure_enrolment': stats.pearsonr(
                state_features['demo_failure_rate'],
                state_features['enrol_total_volume']
            )[0] if len(state_features) > 2 else 0,
        }
        
        # Identify high-risk states (high failure + low enrolment)
        state_features['risk_score'] = (
            state_features['demo_failure_rate'] * 0.4 +
            (100 - state_features['demo_success_rate']) * 0.3 +
            state_features['demo_p99_latency'] / 10 * 0.3
        )
        
        high_risk_states = state_features.nlargest(10, 'risk_score')[
            ['demo_failure_rate', 'demo_p99_latency', 'enrol_total_volume', 'risk_score']
        ]
        
        analysis['high_risk_states'] = high_risk_states
        
        # Insights
        insights = []
        
        if abs(analysis['correlation_failure_youth']) > 0.5:
            direction = "positively" if analysis['correlation_failure_youth'] > 0 else "negatively"
            insights.append(
                f"Auth failure rate is {direction} correlated with youth demographic ratio "
                f"(r={analysis['correlation_failure_youth']:.3f})"
            )
        
        if abs(analysis['correlation_failure_latency']) > 0.5:
            insights.append(
                f"High latency strongly correlates with failure rates "
                f"(r={analysis['correlation_failure_latency']:.3f})"
            )
        
        if abs(analysis['correlation_failure_enrolment']) > 0.3:
            direction = "lower" if analysis['correlation_failure_enrolment'] < 0 else "higher"
            insights.append(
                f"States with higher failure rates tend to have {direction} enrolment volumes"
            )
        
        analysis['insights'] = insights
        
        return analysis
    
    def analyze_enrolment_biometric_relationship(self):
        """
        Analyze relationship between enrolment velocity and biometric update patterns.
        
        Returns:
            dict: Analysis results
        """
        state_features = self.create_state_level_features()
        
        # Correlations
        analysis = {
            'correlation_enrol_bio_volume': stats.pearsonr(
                state_features['enrol_total_volume'],
                state_features['bio_total_volume']
            )[0] if len(state_features) > 2 else 0,
            
            'correlation_enrol_growth_bio_growth': stats.pearsonr(
                state_features['enrol_growth_rate'],
                state_features['bio_daily_avg']
            )[0] if len(state_features) > 2 else 0,
            
            'correlation_infant_enrol_youth_bio': stats.pearsonr(
                state_features['enrol_infant_ratio'],
                state_features['bio_youth_ratio']
            )[0] if len(state_features) > 2 else 0,
        }
        
        # Identify states with mismatched patterns
        state_features['enrol_bio_ratio'] = (state_features['enrol_total_volume'] / 
                                             state_features['bio_total_volume'])
        
        # States with high enrolment but low biometric updates (potential gap)
        state_features['enrol_z'] = (state_features['enrol_total_volume'] - 
                                     state_features['enrol_total_volume'].mean()) / \
                                     state_features['enrol_total_volume'].std()
        state_features['bio_z'] = (state_features['bio_total_volume'] - 
                                   state_features['bio_total_volume'].mean()) / \
                                   state_features['bio_total_volume'].std()
        
        state_features['pattern_mismatch'] = state_features['enrol_z'] - state_features['bio_z']
        
        high_enrol_low_bio = state_features.nlargest(10, 'pattern_mismatch')[
            ['enrol_total_volume', 'bio_total_volume', 'pattern_mismatch']
        ]
        
        analysis['high_enrol_low_bio_states'] = high_enrol_low_bio
        
        # Insights
        insights = []
        
        if analysis['correlation_enrol_bio_volume'] > 0.7:
            insights.append(
                "Strong positive correlation between enrolment and biometric volumes - "
                "states with high enrolment also show high biometric activity"
            )
        elif analysis['correlation_enrol_bio_volume'] < 0.3:
            insights.append(
                "Weak correlation between enrolment and biometric volumes - "
                "enrolment drives may not translate to biometric updates"
            )
        
        if analysis['correlation_infant_enrol_youth_bio'] > 0.5:
            insights.append(
                "States with high infant enrolment also show youth biometric surge - "
                "family enrollment pattern detected"
            )
        
        analysis['insights'] = insights
        
        return analysis
    
    def analyze_latency_geographic_relationship(self):
        """
        Analyze relationship between latency performance and geographic coverage.
        
        Returns:
            dict: Analysis results
        """
        state_features = self.create_state_level_features()
        
        # Correlations
        analysis = {
            'correlation_latency_volume': stats.pearsonr(
                state_features['demo_p99_latency'],
                state_features['demo_total_volume']
            )[0] if len(state_features) > 2 else 0,
            
            'correlation_latency_failure': stats.pearsonr(
                state_features['demo_p99_latency'],
                state_features['demo_failure_rate']
            )[0] if len(state_features) > 2 else 0,
        }
        
        # Identify infrastructure bottleneck states
        state_features['infra_score'] = (
            state_features['demo_p99_latency'] * 0.5 +
            state_features['demo_failure_rate'] * 10 * 0.5
        )
        
        bottleneck_states = state_features.nlargest(10, 'infra_score')[
            ['demo_p99_latency', 'demo_failure_rate', 'demo_total_volume', 'infra_score']
        ]
        
        analysis['infrastructure_bottlenecks'] = bottleneck_states
        
        # Insights
        insights = []
        
        if analysis['correlation_latency_volume'] > 0.5:
            insights.append(
                "High-volume states experience higher latency - "
                "infrastructure scaling required"
            )
        
        if analysis['correlation_latency_failure'] > 0.5:
            insights.append(
                "Strong correlation between latency and failure rate - "
                "timeout-related failures likely"
            )
        
        analysis['insights'] = insights
        
        return analysis
    
    def generate_comprehensive_report(self):
        """
        Generate comprehensive cross-dataset correlation report.
        
        Returns:
            dict: Complete analysis with all relationships
        """
        print("=" * 80)
        print("CROSS-DATASET CORRELATION ANALYSIS")
        print("=" * 80)
        
        report = {}
        
        # State-level features
        report['state_features'] = self.create_state_level_features()
        print(f"✓ Aggregated features for {len(report['state_features'])} states")
        
        # Correlation matrices
        report['pearson_correlation'] = self.calculate_correlation_matrix('pearson')
        report['spearman_correlation'] = self.calculate_correlation_matrix('spearman')
        print(f"✓ Calculated correlation matrices")
        
        # Strong correlations
        report['strong_correlations'] = self.identify_strong_correlations(threshold=0.7)
        print(f"✓ Identified {len(report['strong_correlations'])} strong correlations")
        
        # Specific relationship analyses
        print("\nAnalyzing specific relationships...")
        report['failure_demographic_analysis'] = self.analyze_failure_demographic_relationship()
        report['enrolment_biometric_analysis'] = self.analyze_enrolment_biometric_relationship()
        report['latency_geographic_analysis'] = self.analyze_latency_geographic_relationship()
        
        print("\n" + "=" * 80)
        print("KEY INSIGHTS")
        print("=" * 80)
        
        all_insights = []
        all_insights.extend(report['failure_demographic_analysis'].get('insights', []))
        all_insights.extend(report['enrolment_biometric_analysis'].get('insights', []))
        all_insights.extend(report['latency_geographic_analysis'].get('insights', []))
        
        for i, insight in enumerate(all_insights, 1):
            print(f"{i}. {insight}")
        
        print("=" * 80)
        
        return report


# Quick test
if __name__ == "__main__":
    print("Correlation Engine module loaded successfully!")
    print("Use with actual DataFrames for analysis.")
