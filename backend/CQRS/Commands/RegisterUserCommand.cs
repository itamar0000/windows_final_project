namespace backend.CQRS.Commands
{
    public class RegisterUserCommand
    {
        public string Username { get; set; }
        public string Password { get; set; }
    }
}
