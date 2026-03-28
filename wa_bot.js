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
const PYTHON_PATH = process.env.PYTHON_PATH || "python";

async function connectToWhatsApp(isCLI = false) {
    const { state, saveCreds } = await useMultiFileAuthState("logs/wa_auth_session");
    const { version } = await fetchLatestBaileysVersion();
    
    const sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: !isCLI, // Only show QR if we're in long-polling mode
        markOnlineOnConnect: true,
    });

    sock.ev.on("creds.update", saveCreds);

    return new Promise((resolve, reject) => {
        sock.ev.on("connection.update", async (update) => {
            const { connection, lastDisconnect, qr } = update;
            
            if (qr && !isCLI) {
                console.log("WhatsApp: Scan the QR code below to login:");
                qrcode.generate(qr, { small: true });
            }

            if (connection === "close") {
                const shouldReconnect = lastDisconnect.error?.output?.statusCode !== DisconnectReason.loggedOut;
                if (shouldReconnect && !isCLI) {
                    connectToWhatsApp(isCLI);
                } else {
                    reject(lastDisconnect.error);
                }
            } else if (connection === "open") {
                console.log("WhatsApp: Connection opened successfully! ✅");
                resolve(sock);
            }
        });
    });
}

async function startPolling() {
    const sock = await connectToWhatsApp(false);

    sock.ev.on("messages.upsert", async (m) => {
        if (m.type !== "notify") return;
        const msg = m.messages[0];
        if (!msg.message) return;

        const sender = msg.key.remoteJid;
        const isFromMe = msg.key.fromMe;
        const body = msg.message.conversation || msg.message.extendedTextMessage?.text || "";
        
        if (!body.startsWith("/")) return;

        // Extract sender number
        const senderNumber = sender.split("@")[0];
        const ownerNumber = sock.user.id.split(":")[0];

        // Authorization Check
        // Allow if: sender is in AUTHORIZED_NUMBERS OR it's a message from owner to themselves
        const isAuthorized = AUTHORIZED_NUMBERS.includes(senderNumber) || (isFromMe && senderNumber === ownerNumber);

        if (AUTHORIZED_NUMBERS.length > 0 && !isAuthorized) {
            console.log(`WhatsApp: Unauthorized access attempt from ${senderNumber}`);
            if (!isFromMe) await sock.sendMessage(sender, { text: "💔 Maaf, nomor kamu belum terdaftar di sistem Ayang." });
            return;
        }

        // Avoid infinite loop: don't process commands sent BY the bot account TO others
        // unless it's a command sent TO itself (self-chat)
        if (isFromMe && senderNumber !== ownerNumber) return;

        console.log(`WhatsApp: Received [ ${body} ] from ${senderNumber}${isFromMe ? " (Self)" : ""}`);

        // Handle /start specifically with a better menu
        const cmd = body.split(" ")[0].toLowerCase();
        if (cmd === "/start") {
            let menu = "✨ *KENDALI TRADING WHATSAPP* ✨\n\n";
            menu += "Silakan ketik perintah di bawah ini:\n\n";
            menu += "🎯 */signals daily* - Sinyal Saham\n";
            menu += "📊 */portfolio daily* - Rekap Tabungan\n";
            menu += "🔋 */status* - Kondisi HP\n";
            menu += "📜 */history* - Catatan Transaksi\n";
            menu += "📂 */logs* - Log Sistem\n\n";
            menu += "_Ayang siap membantu menjaga tradingmu!_ 💖";
            await sock.sendMessage(sender, { text: menu });
            return;
        }

        const pythonCmd = `${PYTHON_PATH} telegram_bot.py --cmd "${body}"`;
        exec(pythonCmd, (error, stdout, stderr) => {
            let response = stdout.trim();
            if (error || stderr) {
                console.error(`WhatsApp: Python execution error: ${stderr || error.message}`);
                response = "💔 Waduh, ada gangguan teknis sedikit. Coba lagi nanti ya?";
            }
            if (!response) response = "🌸 Selesai, tapi tidak ada data yang ditemukan.";
            
            sock.sendMessage(sender, { text: response });
        });
    });
}

async function sendNotification(message) {
    console.log(`WhatsApp: Attempting to send broadcast: "${message.substring(0, 20)}..."`);
    try {
        const sock = await connectToWhatsApp(true);
        for (const num of AUTHORIZED_NUMBERS) {
            const jid = `${num}@s.whatsapp.net`;
            await sock.sendMessage(jid, { text: message });
            console.log(`WhatsApp: Notification sent to ${num}`);
        }
        // Small delay to ensure message is sent before closing
        await new Promise(r => setTimeout(r, 2000));
        process.exit(0);
    } catch (err) {
        console.error("WhatsApp: Failed to send notification:", err);
        process.exit(1);
    }
}

// Main Execution
const args = process.argv.slice(2);
if (args.includes("--send")) {
    const msgIdx = args.indexOf("--send") + 1;
    if (args[msgIdx]) {
        sendNotification(args[msgIdx]);
    } else {
        console.error("WhatsApp: No message provided for --send");
        process.exit(1);
    }
} else {
    startPolling().catch(err => console.error("WhatsApp: Bot crashed:", err));
}
