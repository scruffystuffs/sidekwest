use eyre::Result;

pub async fn handle(event: &poise::Event<'_>) -> Result<()> {
    if let poise::Event::Ready { .. } = event {
        eprintln!("Bot ready");
    }
    Ok(())
}
