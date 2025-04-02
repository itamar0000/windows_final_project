namespace backend.CQRS.Queries
{
    public class GetStockHistoryQuery
    {
        public string Symbol { get; set; }
        public string Range { get; set; } // You can leave this or remove it

        public GetStockHistoryQuery(string symbol, string range = null)
        {
            Symbol = symbol;
            Range = range;
        }
    }

}
