const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason,
    fetchLatestBaileysVersion
} = require("@whiskeysockets/baileys");
const { spawn } = require("child_process");
const qrcode = require("qrcode-terminal");
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
        printQRInTerminal: !isCLI,
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

function runPythonCommand(commandText) {
    return new Promise((resolve) => {
        // Securely execution using spawn instead of exec
        const child = spawn(PYTHON_PATH, ["telegram_bot.py", "--cmd", commandText]);
        
        let stdout = "";
        let stderr = "";

        child.stdout.on("data", (data) => { stdout += data; });
        child.stderr.on("data", (data) => { stderr += data; });

        child.on("close", (code) => {
            if (code !== 0 || stderr) {
                console.error(`WhatsApp: Python error (code ${code}): ${stderr}`);
                resolve("💔 Duh sayang, Ayang lagi pusing nih (Error executing command). Coba lagi nanti ya?");
            } else {
                resolve(stdout.trim() || "🌸 Ayang sudah kerjakan, tapi nggak ada laporannya nih...");
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
        const response = await runPythonCommand(body);
        await sock.sendMessage(sender, { text: response });
    });
}

async function sendNotification(message) {
    console.log(`WhatsApp: Broadcasting notification...`);
    try {
        const sock = await connectToWhatsApp(true);
        for (const num of AUTHORIZED_NUMBERS) {
            const jid = `${num}@s.whatsapp.net`;
            await sock.sendMessage(jid, { text: message });
            console.log(`WhatsApp: Sent to ${num}`);
            // Small delay for rate-limiting protection
            await new Promise(r => setTimeout(r, 1000));
        }
        await new Promise(r => setTimeout(r, 1000));
        process.exit(0);
    } catch (err) {
        console.error("WhatsApp: Broadcast failed:", err);
        process.exit(1);
    }
}

// Main
const args = process.argv.slice(2);
if (args.includes("--send")) {
    const msgIdx = args.indexOf("--send") + 1;
    if (args[msgIdx]) sendNotification(args[msgIdx]);
    else process.exit(1);
} else {
    startPolling().catch(err => console.error("WhatsApp Bot crashed:", err));
}
