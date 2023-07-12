#![allow(warnings)]
#![allow(clippy::all)]

use poise::serenity_prelude as serenity;

use eyre::Result;

mod events;

pub struct Data {} // User data, which is stored and accessible in all command invocations
pub type Error = eyre::Error;
pub type Context<'a> = poise::Context<'a, Data, Error>;

/// Displays your or another user's account creation date
#[poise::command(slash_command, ephemeral)]
async fn ping(ctx: Context<'_>) -> Result<()> {
    ctx.say("pong").await?;
    Ok(())
}

#[poise::command(prefix_command)]
async fn register(ctx: Context<'_>) -> Result<()> {
    poise::builtins::register_application_commands_buttons(ctx).await?;
    Ok(())
}

#[tokio::main]
async fn main() {
    dotenv::dotenv().expect("dotenv initialization");
    let discord_token = std::env::var("DISCORD_TOKEN").expect("missing DISCORD_TOKEN");
    poise::Framework::builder()
        .options(poise::FrameworkOptions {
            commands: vec![ping(), register()],
            event_handler: |_ctx, event, _framework, _data| {
                Box::pin(async move { events::handle(event).await })
            },
            prefix_options: poise::PrefixFrameworkOptions {
                mention_as_prefix: true,
                ..Default::default()
            },
            ..Default::default()
        })
        .token(discord_token)
        .intents(
            serenity::GatewayIntents::non_privileged() | serenity::GatewayIntents::MESSAGE_CONTENT,
        )
        .setup(|_ctx, _ready, _framework| Box::pin(async move { Ok(Data {}) }))
        .run()
        .await
        .unwrap();
}
