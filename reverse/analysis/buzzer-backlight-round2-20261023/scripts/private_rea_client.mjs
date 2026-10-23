// Foreground, isolated REA MCP client. Only commands in this private directory.
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire("D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/round3/rea/package.json");
const { Client } = await import(pathToFileURL(require.resolve('@modelcontextprotocol/client')));
const { StdioClientTransport } = await import(pathToFileURL(require.resolve('@modelcontextprotocol/client/stdio')));
const env = { ...process.env,
    JAVA_HOME: 'C:/Program Files/Java/jdk-21.0.10', GHIDRA_INSTALL_DIR: "D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/ghidra",
    REA_ANALYSIS_PROVIDER: 'ghidra', REA_GHIDRA_STARTUP_TIMEOUT_MS: '1800000',
    HOME: join(root,'home'), USERPROFILE: join(root,'home'),
    APPDATA: join(root,'config'), LOCALAPPDATA: join(root,'data'),
    TEMP: join(root,'tmp'), TMP: join(root,'tmp'),
    AP01_PRIVATE_ANALYSIS_CONFIG: join(root,'profile.json')
};
delete env.REA_GHIDRA_LANGUAGE_ID; delete env.REA_GHIDRA_COMPILER_SPEC_ID;
delete env.REA_GHIDRA_SEED_FILE;
const client = new Client({ name: 'ap01-private-analysis', version: '1.0.0' });
const transport = new StdioClientTransport({ command: process.execPath,
    args: ["D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/round3/rea/scripts/rea.mjs",'mcp'], cwd: "D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/round3/rea", env, stderr: 'pipe' });
transport.stderr?.on('data', bytes => {
    const p=join(root,'evidence/private-rea-stderr.log');
    writeFileSync(p, (existsSync(p)?readFileSync(p):Buffer.alloc(0)).toString()+bytes.toString());
});
await client.connect(transport);
const tools = await client.listTools();
writeFileSync(join(root,'evidence/private-rea-tool-schemas.json'),JSON.stringify(tools,null,2));
console.log(JSON.stringify({ready:true, tools:tools.tools.length}));
const handled = new Set();
const deadline=Date.now()+3600000;
try {
    while(Date.now()<deadline) {
        const requestPath=join(root,'request.json');
        if(existsSync(requestPath)) {
            const request=JSON.parse(readFileSync(requestPath,'utf8'));
            if(!handled.has(request.id)) {
                handled.add(request.id);
                if(request.stop) break;
                for(const [index,command] of request.commands.entries()) {

                    const started=Date.now();
                    try {
                        const response=await client.callTool(command,{timeout:1800000,resetTimeoutOnProgress:true});
                        const filename=`${request.id}-${String(index).padStart(3,'0')}.json`;
                        writeFileSync(join(root,'evidence',filename),JSON.stringify(response));
                        if(index%25===0 || response.isError) console.log(JSON.stringify({id:request.id,index,done:true,isError:response.isError??false,ms:Date.now()-started,file:filename}));
                    } catch(error) {
                        writeFileSync(join(root,'evidence',`${request.id}-${index}-error.json`),JSON.stringify({error:String(error),stack:error.stack}));
                        console.log(JSON.stringify({id:request.id,index,error:String(error)}));
                    }
                }
                console.log(JSON.stringify({id:request.id,complete:true}));
            }
        }
        await new Promise(resolve=>setTimeout(resolve,400));
    }
} finally { await client.close(); }
