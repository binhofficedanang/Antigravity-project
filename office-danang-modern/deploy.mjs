import * as ftp from "basic-ftp";
import * as fs from "fs";

async function deploy() {
    const client = new ftp.Client();
    try {
        await client.access({
            host: "office43.vn",
            user: "antigravity@office43.vn",
            password: "Binh1995@",
            secure: false
        });
        
        console.log("Uploading dist folder...");
        await client.uploadFromDir("dist", "/");
        console.log("Deployment successful!");
    } catch(err) {
        console.error(err);
    }
    client.close();
}
deploy();
