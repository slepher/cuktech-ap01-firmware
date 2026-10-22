// Bounded replay of original 0041 UART retry instructions, with declared call fixtures.
// @category AP01.Research
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import com.google.gson.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.HexFormat;

public class Ap01UartRetryReplay0041 extends GhidraScript {
    private static final long START=0xa00eea08L, DONE=0x1004, CALLBACK=0x1000;
    private static final String SHA="972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9";
    private int read(EmulatorHelper e,long a) throws Exception { return e.readMemory(toAddr(a),1)[0]&255; }
    private void put(EmulatorHelper e,long a,int v) { e.writeMemory(toAddr(a),new byte[]{(byte)v}); }
    private void word(EmulatorHelper e,long a,long v) {
        byte[] b=new byte[4]; for(int i=0;i<4;i++) b[i]=(byte)(v>>>(8*i)); e.writeMemory(toAddr(a),b);
    }
    public void run() throws Exception {
        byte[] bytes=new byte[6769704];
        if(currentProgram.getMemory().getBytes(toAddr(0x9ffff000L),bytes)!=bytes.length ||
            !HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes)).equals(SHA))
            throw new IllegalArgumentException("Wrong original ROM mapping or digest");
        int[][] cases={
            // state, wait, attempts, threshold, expected state/wait/attempts, send calls, exhausted
            {0,0,1,2,0,0,1,0,0}, {1,0,1,2,1,0,1,0,0}, {3,0,1,2,3,0,1,0,0},
            {2,0,1,2,2,1,1,0,0}, {2,1,1,2,2,2,2,1,0},
            {2,2,2,2,2,3,3,1,0}, {2,5,5,2,0,6,5,0,1},
            {2,255,1,2,2,0,1,0,0}, {2,9,1,10,2,10,2,1,0},
            {2,10,2,10,2,11,3,1,0}, {2,13,5,10,0,14,5,0,1}
        };
        JsonArray results=new JsonArray();
        for(int index=0;index<cases.length;index++) {
            int[] c=cases[index]; EmulatorHelper e=new EmulatorHelper(currentProgram);
            JsonArray events=new JsonArray(); int build=0,write=0,callback=0,kick=0,steps=0;
            try {
                e.writeRegister("zero",0);e.writeRegister("sp",0x62fd8000L);e.writeRegister("ra",DONE);
                e.writeRegister("s0",0);e.writeRegister("s1",0);
                word(e,0x62fcb6c0L,CALLBACK);put(e,0x62fcb2efL,3);
                put(e,0x62fcb2f0L,c[0]);put(e,0x62fcb2f1L,c[2]);put(e,0x62fcb2f2L,c[1]);put(e,0x62fcb4f8L,c[3]);
                e.writeRegister(e.getPCRegister(),START);
                while(e.readRegister(e.getPCRegister()).longValue()!=DONE && steps++<500) {
                    monitor.checkCancelled();long pc=e.readRegister(e.getPCRegister()).longValue();String event=null;
                    if(pc==0xa01a4ff8L) { build++;event="frame-builder-fixture"; }
                    else if(pc==0xa00ee96cL) { write++;event="write-fixture-no-side-effects"; }
                    else if(pc==0xa00ee9ceL) { kick++;event="queue-kick-fixture"; }
                    else if(pc==CALLBACK) {
                        callback++;event="passive-callback-0x24";
                        if(e.readRegister("a0").intValue()!=0x24 || e.readRegister("a1").signum()!=0 || e.readRegister("a2").signum()!=0)
                            throw new AssertionError("Unexpected event ABI");
                    }
                    if(event!=null) {events.add(event);e.writeRegister(e.getPCRegister(),e.readRegister("ra"));}
                    else if(!e.step(monitor)) throw new AssertionError(e.getLastError());
                }
                if(steps>=500 || read(e,0x62fcb2f0L)!=c[4] || read(e,0x62fcb2f2L)!=c[5] ||
                    read(e,0x62fcb2f1L)!=c[6] || build!=c[7] || write!=c[7] || callback!=c[8] || kick!=c[8] || read(e,0x62fcb2efL)!=3)
                    throw new AssertionError("Retry fixture mismatch at case "+index);
                JsonObject row=new JsonObject();row.addProperty("case",index);row.addProperty("steps",steps);
                row.add("input",new Gson().toJsonTree(new int[]{c[0],c[1],c[2],c[3]}));
                row.add("output",new Gson().toJsonTree(new int[]{c[4],c[5],c[6]}));row.add("events",events);results.add(row);
            } finally {e.dispose();}
        }
        JsonObject out=new JsonObject();out.addProperty("rom_sha256",SHA);out.addProperty("language",currentProgram.getLanguageID().toString());
        out.addProperty("scope","Original retry helper instructions with four explicit passive call fixtures; no UART, hardware, or full-ROM execution");
        out.addProperty("passed",true);out.add("cases",results);
        Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(out));
        println("AP01_UART_RETRY_REPLAY_PASS cases="+cases.length);
    }
}
