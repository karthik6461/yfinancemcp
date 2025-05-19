import json
import yfinance as yf
from typing import Dict, Any, List, Optional

class YahooFinanceMCPServer:
    def __init__(self):
        self.methods = {
            "get_ticker_info": self.get_ticker_info,
            "get_ticker_news": self.get_ticker_news,
            "search_quote": self.search_quote,
            "search_news": self.search_news,
            "get_top_etfs": self.get_top_etfs,
            "get_top_mutual_funds": self.get_top_mutual_funds,
            "get_top_companies": self.get_top_companies,
            "get_top_growth_companies": self.get_top_growth_companies,
            "get_top_performing_companies": self.get_top_performing_companies,
        }

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get("method")
        params = request.get("params", {})
        
        if method in self.methods:
            try:
                result = self.methods[method](**params)
                return {"result": result, "error": None}
            except Exception as e:
                return {"result": None, "error": str(e)}
        else:
            return {"result": None, "error": "Method not found"}

    def get_ticker_info(self, symbol: str) -> Dict[str, Any]:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info

    def get_ticker_news(self, symbol: str) -> List[Dict[str, Any]]:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        return news

    def search_quote(self, query: str, max_results: int = 8) -> List[Dict[str, Any]]:
        ticker = yf.Ticker(query)
        search_results = []
        # This is a simplified implementation - you might want to use a proper search API
        try:
            info = ticker.info
            search_results.append({
                "symbol": info.get("symbol"),
                "name": info.get("shortName"),
                "exchange": info.get("exchange"),
                "type": info.get("quoteType")
            })
        except:
            pass
        return search_results[:max_results]

    def search_news(self, query: str, news_count: int = 8) -> List[Dict[str, Any]]:
        # Simplified news search - in a real implementation you'd use a proper news API
        ticker = yf.Ticker(query)
        news = ticker.news
        return news[:news_count]

    def get_top_etfs(self, sector: str) -> List[Dict[str, Any]]:
        # Placeholder implementation - in a real app you'd query a proper ETF database
        return [{"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust"}]

    def get_top_mutual_funds(self, sector: str) -> List[Dict[str, Any]]:
        # Placeholder implementation
        return [{"symbol": "VFINX", "name": "Vanguard 500 Index Fund"}]

    def get_top_companies(self, sector: str, top_n: int) -> List[Dict[str, Any]]:
        # Placeholder implementation
        return [{"symbol": "AAPL", "name": "Apple Inc."}]

    def get_top_growth_companies(self, sector: str, top_n: int) -> List[Dict[str, Any]]:
        # Placeholder implementation
        return [{"symbol": "TSLA", "name": "Tesla Inc."}]

    def get_top_performing_companies(self, sector: str, top_n: int) -> List[Dict[str, Any]]:
        # Placeholder implementation
        return [{"symbol": "NVDA", "name": "NVIDIA Corporation"}]

if __name__ == "__main__":
    import sys
    server = YahooFinanceMCPServer()
    
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.process_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except json.JSONDecodeError:
            print(json.dumps({"result": None, "error": "Invalid JSON input"}))
            sys.stdout.flush()