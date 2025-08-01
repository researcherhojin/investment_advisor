-- AI Investment Advisory System Database Schema
-- This script initializes the PostgreSQL database for the modernized system

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS investment;
CREATE SCHEMA IF NOT EXISTS cache;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Set search path
SET search_path TO investment, public;

-- Users and authentication (future)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Stock information
CREATE TABLE IF NOT EXISTS stocks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    market VARCHAR(10) NOT NULL CHECK (market IN ('US', 'KR')),
    sector VARCHAR(100),
    industry VARCHAR(200),
    exchange VARCHAR(50),
    currency VARCHAR(3),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, market)
);

-- Price history
CREATE TABLE IF NOT EXISTS price_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    open_price DECIMAL(15, 4),
    high_price DECIMAL(15, 4),
    low_price DECIMAL(15, 4),
    close_price DECIMAL(15, 4) NOT NULL,
    volume BIGINT,
    adjusted_close DECIMAL(15, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, date)
);

-- Financial data
CREATE TABLE IF NOT EXISTS financial_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
    period VARCHAR(10) NOT NULL, -- Q1, Q2, Q3, Q4, FY
    year INTEGER NOT NULL,
    revenue DECIMAL(20, 2),
    net_income DECIMAL(20, 2),
    total_assets DECIMAL(20, 2),
    total_equity DECIMAL(20, 2),
    total_debt DECIMAL(20, 2),
    free_cash_flow DECIMAL(20, 2),
    pe_ratio DECIMAL(10, 2),
    pb_ratio DECIMAL(10, 2),
    roe DECIMAL(8, 4),
    roa DECIMAL(8, 4),
    debt_to_equity DECIMAL(8, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, period, year)
);

-- Analysis sessions
CREATE TABLE IF NOT EXISTS analysis_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
    session_data JSONB NOT NULL,
    analysis_period INTEGER DEFAULT 12,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT
);

-- Agent analysis results
CREATE TABLE IF NOT EXISTS agent_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    agent_type VARCHAR(50) NOT NULL,
    agent_weight DECIMAL(4, 3) DEFAULT 1.0,
    analysis_result TEXT NOT NULL,
    confidence_score DECIMAL(4, 3),
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Final investment decisions
CREATE TABLE IF NOT EXISTS investment_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    decision VARCHAR(10) NOT NULL CHECK (decision IN ('BUY', 'SELL', 'HOLD')),
    confidence DECIMAL(4, 3) NOT NULL,
    rationale TEXT NOT NULL,
    price_target DECIMAL(15, 4),
    stop_loss DECIMAL(15, 4),
    time_horizon VARCHAR(20),
    risk_level VARCHAR(10) CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Cache schema tables
CREATE TABLE IF NOT EXISTS cache.api_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    data JSONB NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Analytics schema tables
CREATE TABLE IF NOT EXISTS analytics.user_activity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    activity_type VARCHAR(50) NOT NULL,
    activity_data JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Performance tracking
CREATE TABLE IF NOT EXISTS analytics.performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15, 6) NOT NULL,
    metric_unit VARCHAR(20),
    tags JSONB,
    measured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_stocks_ticker_market ON stocks(ticker, market);
CREATE INDEX IF NOT EXISTS idx_stocks_sector ON stocks(sector);
CREATE INDEX IF NOT EXISTS idx_price_history_stock_date ON price_history(stock_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_price_history_date ON price_history(date DESC);
CREATE INDEX IF NOT EXISTS idx_financial_data_stock_year ON financial_data(stock_id, year DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_user_created ON analysis_sessions(user_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_stock ON analysis_sessions(stock_id);
CREATE INDEX IF NOT EXISTS idx_agent_analyses_session ON agent_analyses(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_analyses_type ON agent_analyses(agent_type);
CREATE INDEX IF NOT EXISTS idx_investment_decisions_session ON investment_decisions(session_id);
CREATE INDEX IF NOT EXISTS idx_api_cache_key ON cache.api_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_api_cache_expires ON cache.api_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_activity_user_time ON analytics.user_activity(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_name_time ON analytics.performance_metrics(metric_name, measured_at DESC);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_data ON analysis_sessions USING GIN(session_data);
CREATE INDEX IF NOT EXISTS idx_api_cache_data ON cache.api_cache USING GIN(data);
CREATE INDEX IF NOT EXISTS idx_user_activity_data ON analytics.user_activity USING GIN(activity_data);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_tags ON analytics.performance_metrics USING GIN(tags);

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_stocks_updated_at BEFORE UPDATE ON stocks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_financial_data_updated_at BEFORE UPDATE ON financial_data FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to clean expired cache entries
CREATE OR REPLACE FUNCTION cache.clean_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM cache.api_cache WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Insert sample data for development
INSERT INTO stocks (ticker, name, market, sector, industry, exchange, currency) VALUES
    ('AAPL', 'Apple Inc.', 'US', 'Technology', 'Consumer Electronics', 'NASDAQ', 'USD'),
    ('GOOGL', 'Alphabet Inc.', 'US', 'Technology', 'Internet Content & Information', 'NASDAQ', 'USD'),
    ('MSFT', 'Microsoft Corporation', 'US', 'Technology', 'Software Infrastructure', 'NASDAQ', 'USD'),
    ('TSLA', 'Tesla, Inc.', 'US', 'Consumer Cyclical', 'Auto Manufacturers', 'NASDAQ', 'USD'),
    ('005930.KS', '삼성전자', 'KR', 'Technology', 'Consumer Electronics', 'KRX', 'KRW'),
    ('000660.KS', 'SK하이닉스', 'KR', 'Technology', 'Semiconductors', 'KRX', 'KRW'),
    ('035420.KS', 'NAVER', 'KR', 'Technology', 'Internet Content & Information', 'KRX', 'KRW'),
    ('051910.KS', 'LG화학', 'KR', 'Basic Materials', 'Specialty Chemicals', 'KRX', 'KRW')
ON CONFLICT (ticker, market) DO NOTHING;

-- Grant permissions
GRANT USAGE ON SCHEMA investment TO stock_user;
GRANT USAGE ON SCHEMA cache TO stock_user;
GRANT USAGE ON SCHEMA analytics TO stock_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA investment TO stock_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA cache TO stock_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO stock_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA investment TO stock_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA cache TO stock_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA analytics TO stock_user;

-- Create a view for easy stock lookup
CREATE OR REPLACE VIEW stock_summary AS
SELECT 
    s.id,
    s.ticker,
    s.name,
    s.market,
    s.sector,
    s.industry,
    s.exchange,
    s.currency,
    ph.close_price as latest_price,
    ph.date as latest_price_date,
    fd.pe_ratio,
    fd.pb_ratio,
    fd.roe
FROM stocks s
LEFT JOIN LATERAL (
    SELECT close_price, date 
    FROM price_history 
    WHERE stock_id = s.id 
    ORDER BY date DESC 
    LIMIT 1
) ph ON true
LEFT JOIN LATERAL (
    SELECT pe_ratio, pb_ratio, roe 
    FROM financial_data 
    WHERE stock_id = s.id 
    ORDER BY year DESC, period DESC 
    LIMIT 1
) fd ON true
WHERE s.is_active = true;

GRANT SELECT ON stock_summary TO stock_user;