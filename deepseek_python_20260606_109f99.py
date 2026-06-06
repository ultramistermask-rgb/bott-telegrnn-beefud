from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
import asyncio
from pathlib import Path

# Configurar logging (apenas erros críticos)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR  # Mude para ERROR para evitar logs desnecessários
)
logger = logging.getLogger(__name__)

# Token do bot
API_TOKEN = '8625819972:AAEbrdWoxz8TCXSOk6n-UMfRknYXcCHPM6M'

# Dicionário para armazenar os níveis dos usuários
user_levels = {}

# Cache para imagens (carrega uma vez e reutiliza)
image_cache = {}

def load_image_to_cache(image_path):
    """Carrega imagem para cache se ainda não estiver carregada"""
    if image_path not in image_cache:
        try:
            with open(image_path, 'rb') as f:
                image_cache[image_path] = f.read()
            return True
        except FileNotFoundError:
            return False
    return True

# Pré-carregar imagens ao iniciar
def preload_images():
    """Pré-carrega todas as imagens necessárias"""
    images = ['boasvindas.png'] + [f'info_n{i}.png' for i in range(1, 11)]
    for img in images:
        load_image_to_cache(img)
        logger.info(f"Carregada imagem: {img}")

# Comando /start otimizado
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Responde imediatamente para evitar timeout
    await update.message.chat.send_action(action="typing")
    
    try:
        # Envia a imagem de boas-vindas usando cache
        image_data = image_cache.get('boasvindas.png')
        if image_data:
            await update.message.reply_photo(
                photo=image_data,
                write_timeout=30,
                read_timeout=30,
                connect_timeout=30
            )
        else:
            await update.message.reply_text("⚠️ Imagem não encontrada")
            return
        
        # Cria os botões de nível (1 a 10)
        keyboard = []
        
        # Adiciona botões em 2 linhas de 5
        for i in range(0, 10, 5):
            row = []
            for j in range(1, 6):
                nivel = i + j
                if nivel <= 10:
                    button = InlineKeyboardButton(f"👑 NÍVEL {nivel}", callback_data=f'nivel_{nivel}')
                    row.append(button)
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Envia a mensagem com os botões
        await update.message.reply_text(
            "📊 **QUAL É O SEU NÍVEL?**\nSelecione uma das opções abaixo:",
            reply_markup=reply_markup,
            parse_mode='Markdown',
            write_timeout=30,
            read_timeout=30
        )
        
    except Exception as e:
        logger.error(f"Erro no start: {str(e)}")
        # Não envia mensagem de erro para o usuário

# Handler para os botões de nível otimizado
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # Responde instantaneamente ao callback
    await query.answer()
    
    try:
        # Extrai o número do nível
        level = int(query.data.split('_')[1])
        
        # Envia a imagem específica do nível usando cache
        image_name = f'info_n{level}.png'
        image_data = image_cache.get(image_name)
        
        if image_data:
            await query.message.reply_photo(
                photo=image_data,
                write_timeout=30,
                read_timeout=30
            )
        else:
            await query.message.reply_text(f"⚠️ Conteúdo do nível {level} indisponível")
            return
        
        # Links personalizados para cada nível
        links = {
            1: "https://exemplo.com/nivel1",
            2: "https://exemplo.com/nivel2",
            3: "https://exemplo.com/nivel3",
            4: "https://exemplo.com/nivel4",
            5: "https://exemplo.com/nivel5",
            6: "https://exemplo.com/nivel6",
            7: "https://exemplo.com/nivel7",
            8: "https://exemplo.com/nivel8",
            9: "https://exemplo.com/nivel9",
            10: "https://exemplo.com/nivel10"
        }
        
        # Cria botão com link
        keyboard = [[InlineKeyboardButton(
            "🔗 ACESSAR CONTEÚDO EXCLUSIVO 🔗",
            url=links.get(level, "https://exemplo.com")
        )]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Envia mensagem com botão
        await query.message.reply_text(
            f"✨ **NÍVEL {level}!** ✨\nClique abaixo para acessar:",
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True  # Desativa preview de links para acelerar
        )
        
        # Armazena nível do usuário
        user_levels[query.from_user.id] = level
        
    except Exception as e:
        logger.error(f"Erro no callback: {str(e)}")
        # Não mostra erro para o usuário

# Comando menu otimizado
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# Comando meu nível
async def my_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in user_levels:
        level = user_levels[user_id]
        await update.message.reply_text(
            f"🎯 Seu nível: **{level}**\nUse /menu para voltar.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❓ Use /start para selecionar seu nível."
        )

# Handler para erros silencioso
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trata erros silenciosamente sem enviar mensagens ao usuário"""
    logger.error(f"Erro: {context.error}")
    # Não envia mensagem para o usuário

def main():
    """Função principal otimizada"""
    
    # Pré-carrega todas as imagens
    print("🖼️ Pré-carregando imagens...")
    preload_images()
    print("✅ Imagens carregadas na memória!")
    
    # Configura a aplicação com timeouts maiores
    application = (
        Application.builder()
        .token(API_TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .pool_timeout(30.0)
        .build()
    )
    
    # Adiciona handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("meunivel", my_level))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)
    
    print("🤖 Bot iniciado com sucesso!")
    print("⚡ Modo otimizado ativado")
    print("Pressione Ctrl+C para parar.")
    
    # Inicia o bot com polling mais rápido
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,  # Ignora updates pendentes
        timeout=30
    )

if __name__ == '__main__':
    main()