const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason,
    fetchLatestBaileysVersion,
    makeCacheableSignalKeyStore
} = require("@whiskeysockets/baileys");
const { exec } = require("child_process");
const qrcode = require("qrcode-terminal");
const fs = require("fs");
const path = require("path");
require("dotenv").config();

// Configuration
const AUTHORIZED_NUMBERS = process.env.WHATSAPP_AUTHORIZED_NUMBERS ? process.env.WHATSAPP_AUTHORIZED_NUMBERS.split(",") : [];
const PYTHON_PATH = process.env.PYTHON_PATH || "python"; // Fallback to system python

async function startBot() {
    const { state, saveCreds } = await useMultiFileAuthState("logs/wa_auth_session");
    const { version, isLatest } = await fetchLatestBaileysVersion();
    
    console.log(`WhatsApp: Using Baileys v${version.join(".")}, isLatest: ${isLatest}`);

    const sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: true,
        markOnlineOnConnect: true,
    });

    sock.ev.on("creds.update", saveCreds);

    sock.ev.on("connection.update", (update) => {
        const { connection, lastDisconnect, qr } = update;
        if (qr) {
            console.log("WhatsApp: Scan the QR code below to login:");
            qrcode.generate(qr, { small: true });
        }
        if (connection === "close") {
            const shouldReconnect = lastDisconnect.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log("WhatsApp: Connection closed. Reconnecting...", shouldReconnect);
            if (shouldReconnect) startBot();
        } else if (connection === "open") {
            console.log("WhatsApp: Connection opened successfully! ✅");
        }
    });

    sock.ev.on("messages.upsert", async (m) => {
        if (m.type !== "notify") return;
        const msg = m.messages[0];
        if (!msg.message || msg.key.fromMe) return;

        const sender = msg.key.remoteJid;
        const body = msg.message.conversation || msg.message.extendedTextMessage?.text || "";
        
        if (!body.startsWith("/")) return;

        // Check Authorization
        const senderNumber = sender.split("@")[0];
        if (AUTHORIZED_NUMBERS.length > 0 && !AUTHORIZED_NUMBERS.includes(senderNumber)) {
            console.log(`WhatsApp: Unauthorized access attempt from ${senderNumber}`);
            await sock.sendMessage(sender, { text: "💔 Maaf sayang, nomor kamu belum terdaftar di hati Ayang..." });
            return;
        }

        console.log(`WhatsApp: Received [ ${body} ] from ${senderNumber}`);

        // Bridge to Python
        const pythonCmd = `${PYTHON_PATH} telegram_bot.py --cmd "${body}"`;
        exec(pythonCmd, (error, stdout, stderr) => {
            let response = stdout.trim();
            if (error || stderr) {
                console.error(`WhatsApp: Python execution error: ${stderr || error.message}`);
                response = "💔 Duh sayang, Ayang lagi pusing nih (Error executing command). Coba lagi nanti ya?";
            }
            if (!response) response = "🌸 Ayang sudah kerjakan, tapi nggak ada laporannya nih...";

            // Clean up Markdown for WhatsApp (mostly bold)
            // Telegram uses *text* for bold, WA uses *text* too.
            // But Telegram uses _text_ for italic, WA uses _text_ too.
            // Some differences in multi-line code blocks, but we'll try raw first.
            
            sock.sendMessage(sender, { text: response });
        });
    });
}

startBot().catch(err => console.error("WhatsApp: Bot crashed:", err));
