const express = require("express");
const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require("@whiskeysockets/baileys");
const qrcode = require("qrcode-terminal");
const axios = require("axios");

const app = express();
app.use(express.json());

let sock;

async function start() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
    
    sock = makeWASocket({
        auth: state,
        printQRInTerminal: true
    });

    sock.ev.on("creds.update", saveCreds);

    // DEBUG: Log ALL events to find the missing YES
    sock.ev.process(async (events) => {
        if (events["messages.upsert"]) {
            const m = events["messages.upsert"];
            // Original logic handles this, but we'll log it here too
            // console.log("EVENT messages.upsert:", JSON.stringify(m, null, 2));
        }
        if (events["messages.update"]) {
            console.log("EVENT messages.update:", JSON.stringify(events["messages.update"], null, 2));
        }
    });

    sock.ev.on("connection.update", (update) => {
        const { connection, lastDisconnect, qr } = update;
        if (qr) {
            console.log("Scan this QR code to login:");
            qrcode.generate(qr, { small: true });
        }
        if (connection === "close") {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log("Connection closed due to ", lastDisconnect.error, ", reconnecting ", shouldReconnect);
            if (shouldReconnect) start();
        } else if (connection === "open") {
            console.log("WhatsApp Connection opened");
        }
    });

    sock.ev.on("messages.upsert", async m => {
        const msg = m.messages[0];
        if (!msg.message) return;

        const sender = msg.key.remoteJid;
        const fromMe = msg.key.fromMe;

        // Ignore Group Messages
        if (sender.endsWith("@g.us")) {
            return;
        }

        // Ultra-Robust Text Extraction
        const text = 
            msg.message?.conversation || 
            msg.message?.extendedTextMessage?.text || 
            msg.message?.imageMessage?.caption || 
            msg.message?.videoMessage?.caption || 
            msg.message?.buttonsResponseMessage?.selectedButtonId || 
            msg.message?.listResponseMessage?.title || 
            "";

        console.log(`WHATSAPP from ${sender} (fromMe: ${fromMe}):`, text);

        if (fromMe) {
            const clean = text.toLowerCase().trim();
            if (clean === "yes" || clean === "no" || clean.startsWith("edit") || clean.startsWith("/")) {
                console.log("Detected command fromMe (linked device):", text);
            } else {
                return;
            }
        }

        console.log("RAW MESSAGE:", JSON.stringify(msg, null, 2));

        // Send to Python (local bridge)
        try {
            await axios.post("http://localhost:5000/whatsapp", { 
                text: text,
                sender: sender,
                id: msg.key.id // For deduplication
            });
        } catch (error) {
            console.error("Error sending to Python bridge:", error.message);
        }
    });
}

app.post("/send", async (req, res) => {
    const { number, message } = req.body;
    
    if (!sock) {
        return res.status(500).json({ status: "error", message: "WhatsApp not connected" });
    }

    try {
        const jid = number.includes("@s.whatsapp.net") ? number : `${number}@s.whatsapp.net`;
        await sock.sendMessage(jid, {
            text: message
        });
        res.json({ status: "sent" });
    } catch (error) {
        res.status(500).json({ status: "error", message: error.message });
    }
});

const PORT = 3001;
app.listen(PORT, () => {
    console.log(`WhatsApp API running on port ${PORT}`);
    start();
});
