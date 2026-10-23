// Offline replay of the original response handler; no device or UART access.
// @category AP01.Research
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import com.google.gson.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

public class Ap01UartResponseReplay0041 extends GhidraScript {
    private static final String SHA="972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9";
    private void word(EmulatorHelper e,long a,long v) {
        byte[] b=new byte[4];for(int i=0;i<4;i++)b[i]=(byte)(v>>>(8*i));e.writeMemory(toAddr(a),b);
    }
    public void run() throws Exception {
        Path output=Path.of(getScriptArgs()[0]);
        if(Files.exists(output))throw new IllegalArgumentException("Refusing to overwrite replay evidence");
        byte[] image=new byte[6769704];
        if(currentProgram.getMemory().getBytes(toAddr(0x9ffff000L),image)!=image.length ||
            !HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(image)).equals(SHA))throw new IllegalArgumentException("Wrong ROM");
        if(!currentProgram.getLanguageID().toString().equals("RISCV:LE:32:ap01thead3"))throw new IllegalArgumentException("Wrong processor model");
        // cmd, length, null payload, context present, interface index, changed data, endpoint
        // endpoint: 0 return; 1 first payload read; 2 lookup; 3 explicit zero-read; 5 fixed-size memcmp entry
        int[][] cases={{0x52,0,1,1,0,0,1},{0x52,1,0,1,0,0,2},{0x52,0,0,1,0,0,2},
            {0x56,12,0,1,0,1,0},{0x56,13,0,1,0,0,0},{0x56,13,0,1,0,1,0},
            {0x56,13,0,1,1,0,0},{0x56,13,0,1,1,1,3},{0x56,13,0,0,0,1,3},
            {0xd1,0,1,1,0,0,5},{0x55,0,1,1,0,0,5},{0x57,0,1,1,0,0,5},
            {0x58,0,1,1,0,0,5},{0x5e,0,1,1,0,0,5}};
        JsonArray rows=new JsonArray();
        for(int index=0;index<cases.length;index++) {
            int[] c=cases[index];EmulatorHelper e=new EmulatorHelper(currentProgram);JsonObject row=new JsonObject();
            JsonArray calls=new JsonArray();int endpoint=-1,steps=0,copies=0;long copyDest=-1;
            try {
                for(String n:"zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5 a6 a7 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 t3 t4 t5 t6".split(" "))e.writeRegister(n,0);
                e.writeMemory(toAddr(0x62fc0000L),new byte[0x20000]);
                // Explicit readable/writable zero-page fixture; this does NOT model hardware fault behavior.
                e.writeMemory(toAddr(0),new byte[0x1000]);
                word(e,0x62fcb2ccL,c[3]!=0?0x62fd0000L:0);word(e,0x62fd0000L,0x62fd1000L);
                e.writeMemory(toAddr(0x62fd0006L),new byte[]{1});
                byte[] payload=new byte[40];payload[0]=(byte)c[4];if(c[5]!=0)payload[5]=0x11;
                e.writeMemory(toAddr(0x62fd4000L),payload);
                e.writeRegister("sp",0x62fd8000L);e.writeRegister("ra",0x1004);
                e.writeRegister("a0",c[0]);e.writeRegister("a1",c[1]);e.writeRegister("a2",c[2]!=0?0:0x62fd4000L);
                e.writeRegister(e.getPCRegister(),0xa00a8582L);
                while(steps++<10000) {
                    monitor.checkCancelled();long pc=e.readRegister(e.getPCRegister()).longValue();
                    if(pc==0x1004){endpoint=0;break;}
                    if(pc==0xa00a8626L && c[6]==1){endpoint=1;break;}
                    if(pc==0xa00a53c0L){endpoint=2;break;}
                    if(pc==0xa00a9d18L){endpoint=3;break;}
                    if(pc==0xa00501beL || pc==0xa000589cL) {
                        JsonObject call=new JsonObject();call.addProperty("pc",Long.toHexString(pc));
                        for(String n:new String[]{"a0","a1","a2"})call.addProperty(n,e.readRegister(n).longValue());calls.add(call);
                        if(pc==0xa00501beL && c[6]==5){endpoint=5;break;}
                        if(pc==0xa000589cL){copies++;copyDest=e.readRegister("a0").longValue();}
                    }
                    // Passive notifications and scheduling only. memcmp and memcpy execute original instructions.
                    if(pc==0xa008b51aL || pc==0xa00a389cL || pc==0xa01b2804L) {
                        e.writeRegister(e.getPCRegister(),e.readRegister("ra"));continue;
                    }
                    if(!e.step(monitor))throw new AssertionError("case="+index+" pc="+Long.toHexString(pc)+" "+e.getLastError());
                }
                if(endpoint!=c[6])throw new AssertionError("case="+index+" endpoint="+endpoint);
                int expectedCopies=(c[0]==0x56 && c[1]==13 && c[5]!=0)?1:0;
                if(copies!=expectedCopies)throw new AssertionError("Unexpected copy count");
                if(expectedCopies!=0 && copyDest!=(c[3]!=0 && c[4]==0?0x62fd1018L:0))throw new AssertionError("Unexpected copy destination");
                if(endpoint==1 && e.readRegister("a2").signum()!=0)throw new AssertionError("Expected NULL payload read");
                if(endpoint==5) {
                    int expected=c[0]==0xd1?7:c[0]==0x55?24:c[0]==0x57?6:c[0]==0x58?4:3;
                    if(e.readRegister("a2").intValue()!=expected || e.readRegister("a1").signum()!=0)throw new AssertionError("Unexpected fixed-size NULL comparison");
                    row.addProperty("requested_copy_bytes",expected);
                }
                row.addProperty("case",index);row.add("input",new Gson().toJsonTree(c));row.addProperty("steps",steps);
                row.addProperty("endpoint",endpoint);row.addProperty("stop_pc",e.readRegister(e.getPCRegister()).toString(16));
                row.addProperty("memcpy_calls",copies);if(copies!=0)row.addProperty("memcpy_destination",Long.toHexString(copyDest));
                row.add("memory_calls",calls);rows.add(row);
            } finally {e.dispose();}
        }
        JsonObject out=new JsonObject();out.addProperty("rom_sha256",SHA);out.addProperty("language",currentProgram.getLanguageID().toString());
        out.addProperty("passed",true);out.addProperty("scope","Original normal-response dispatcher and fixed-copy helper; original memcmp/memcpy execute for 0x56 cases. Synthetic RAM includes writable zero page; log/notification/scheduler calls use passive fixtures. Stop before first NULL payload read, fixed-size memcmp with NULL source, or explicit terminal zero-read as declared. No parser/UART/hardware/full-ROM execution.");
        out.add("cases",rows);Files.writeString(output,new GsonBuilder().setPrettyPrinting().create().toJson(out));
        println("AP01_UART_RESPONSE_REPLAY_PASS cases="+cases.length);
    }
}
