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
        if (!msg.message || msg.key.fromMe) return;

        const sender = msg.key.remoteJid;
        const body = msg.message.conversation || msg.message.extendedTextMessage?.text || "";
        
        if (!body.startsWith("/")) return;

        const senderNumber = sender.split("@")[0];
        if (AUTHORIZED_NUMBERS.length > 0 && !AUTHORIZED_NUMBERS.includes(senderNumber)) {
            console.log(`WhatsApp: Unauthorized access attempt from ${senderNumber}`);
            await sock.sendMessage(sender, { text: "💔 Maaf sayang, nomor kamu belum terdaftar di hati Ayang..." });
            return;
        }

        console.log(`WhatsApp: Received [ ${body} ] from ${senderNumber}`);

        const pythonCmd = `${PYTHON_PATH} telegram_bot.py --cmd "${body}"`;
        exec(pythonCmd, (error, stdout, stderr) => {
            let response = stdout.trim();
            if (error || stderr) {
                console.error(`WhatsApp: Python execution error: ${stderr || error.message}`);
                response = "💔 Duh sayang, Ayang lagi pusing nih (Error executing command). Coba lagi nanti ya?";
            }
            if (!response) response = "🌸 Ayang sudah kerjakan, tapi nggak ada laporannya nih...";
            
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
