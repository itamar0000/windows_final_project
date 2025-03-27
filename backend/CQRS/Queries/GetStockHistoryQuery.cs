namespace backend.CQRS.Queries
{
    public class GetStockHistoryQuery
    {
        public string Symbol { get; set; }
        public string Range { get; set; }

        public GetStockHistoryQuery(string symbol, string range)
        {
            Symbol = symbol;
            Range = range;
        }
    }
}
