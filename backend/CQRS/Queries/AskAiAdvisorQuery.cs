namespace backend.CQRS.Queries
{
    public class AiAdvisorQuery
    {
        public string Question { get; set; }

        public AiAdvisorQuery(string question)
        {
            Question = question;
        }
    }
}
