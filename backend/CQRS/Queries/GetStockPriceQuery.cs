namespace backend.CQRS.Queries
{
    public class GetStockPriceQuery
    {
        public string Symbol { get; set; }

        public GetStockPriceQuery(string symbol)
        {
            Symbol = symbol;
        }
    }
}
