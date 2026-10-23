// Original parser -> CRC -> ordinary response dispatcher, synthetic UART/RAM only.
// @category AP01.Research
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import com.google.gson.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

public class Ap01UartEndToEndReplay0041 extends GhidraScript {
    private void word(EmulatorHelper e,long a,long v) {byte[] b=new byte[4];for(int i=0;i<4;i++)b[i]=(byte)(v>>>(8*i));e.writeMemory(toAddr(a),b);}
    private void byteAt(EmulatorHelper e,long a,int v) {e.writeMemory(toAddr(a),new byte[]{(byte)v});}
    private byte[] frame(int cmd,int declared,byte[] payload) {
        byte[] body=new byte[3+payload.length];body[1]=(byte)cmd;body[2]=(byte)declared;System.arraycopy(payload,0,body,3,payload.length);
        int crc=0;for(byte v:body){crc^=(v&255)<<8;for(int j=0;j<8;j++)crc=((crc<<1)^((crc&0x8000)!=0?0x1021:0))&65535;}
        ArrayList<Byte> out=new ArrayList<>();out.add((byte)0xa5);
        for(int i=0;i<body.length+2;i++){int v=i<body.length?body[i]&255:(i==body.length?crc&255:crc>>>8);if(v==0xa5||v==0x5a||v==0xaa)out.add((byte)0xaa);out.add((byte)v);}
        out.add((byte)0x5a);byte[] result=new byte[out.size()];for(int i=0;i<result.length;i++)result[i]=out.get(i);return result;
    }
    public void run() throws Exception {
        Path output=Path.of(getScriptArgs()[0]);if(Files.exists(output))throw new IllegalArgumentException("Existing evidence");
        String sha="972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9";
        byte[] image=new byte[6769704];if(currentProgram.getMemory().getBytes(toAddr(0x9ffff000L),image)!=image.length ||
            !HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(image)).equals(sha))throw new IllegalArgumentException("Wrong ROM");
        if(!currentProgram.getLanguageID().toString().equals("RISCV:LE:32:ap01thead3"))throw new IllegalArgumentException("Wrong model");
        // cmd, declared len, actual payload size, interface index, changed data, context present, endpoint
        // endpoint: 1 before NULL payload read; 3 before terminal zero read; 5 before NULL memcmp; 6 parser resumes after callback.
        int[][] cases={{0x52,0,0,0,0,1,1},{0xd1,0,0,0,0,1,5},{0x55,0,0,0,0,1,5},
            {0x57,0,0,0,0,1,5},{0x58,0,0,0,0,1,5},{0x5e,0,0,0,0,1,5},
            {0x56,12,12,0,1,1,6},{0x56,13,13,0,1,1,6},{0x56,13,13,1,1,1,3},
            {0x56,13,13,0,1,0,3},{0x56,13,0,0,0,1,6}};
        JsonArray rows=new JsonArray();
        for(int index=0;index<cases.length;index++) {
            int[] c=cases[index];byte[] payload=new byte[c[2]];if(payload.length>0)payload[0]=(byte)c[3];if(payload.length>5&&c[4]!=0)payload[5]=0x11;
            byte[] wire=frame(c[0],c[1],payload);EmulatorHelper e=new EmulatorHelper(currentProgram);
            int cursor=0,steps=0,crcCalls=0,endpoint=-1,parserCopy=-1,handlerCopies=0;long resume=-1,destination=-1;boolean entered=false;
            JsonObject row=new JsonObject();JsonArray calls=new JsonArray();
            try {
                for(String n:"zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5 a6 a7 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 t3 t4 t5 t6".split(" "))e.writeRegister(n,0);
                e.writeMemory(toAddr(0x62fc0000L),new byte[0x20000]);
                // Writable zero page deliberately models no hardware exception policy.
                e.writeMemory(toAddr(0),new byte[0x1000]);
                byte[] source=new byte[0x110];Arrays.fill(source,(byte)0xa6);e.writeMemory(toAddr(0x62fcb458L),source);
                byteAt(e,0x62fcb487L,0);byteAt(e,0x62fcb488L,0);byteAt(e,0x62fcb489L,0);
                byteAt(e,0x62fcb2f0L,2);byteAt(e,0x62fcb2f3L,c[0]);
                word(e,0x62fcb6c0L,0xa00a8582L);word(e,0x62fc91b0L,7);word(e,0x62fd7000L,11);
                word(e,0x62fcb2ccL,c[5]!=0?0x62fd0000L:0);word(e,0x62fd0000L,0x62fd1000L);byteAt(e,0x62fd0006L,1);
                e.writeRegister("sp",0x62fd8000L);e.writeRegister("ra",0x1004);e.writeRegister("a2",1);e.writeRegister(e.getPCRegister(),0xa00a8330L);
                while(steps++<30000) {
                    monitor.checkCancelled();long pc=e.readRegister(e.getPCRegister()).longValue();
                    if(entered&&pc==resume){endpoint=6;break;}
                    if(pc==0xa00a8582L){entered=true;resume=e.readRegister("ra").longValue();
                        row.addProperty("callback_cmd",e.readRegister("a0").intValue());row.addProperty("callback_length",e.readRegister("a1").intValue());row.addProperty("callback_payload",e.readRegister("a2").toString(16));}
                    if(entered&&pc==0xa00a8626L&&c[6]==1){endpoint=1;break;}
                    if(entered&&pc==0xa00a9d18L){endpoint=3;break;}
                    if(pc==0x1004)break;
                    if(pc==0xa003f6a2L){
                        if(e.readRegister("a0").intValue()!=7||e.readRegister("a2").intValue()!=1)throw new AssertionError("Unexpected read API");
                        if(cursor<wire.length){byteAt(e,e.readRegister("a1").longValue(),wire[cursor++]&255);e.writeRegister("a0",1);}else e.writeRegister("a0",0xffffffffL);
                        e.writeRegister(e.getPCRegister(),e.readRegister("ra"));continue;
                    }
                    if(pc==0xa00267c0L){e.writeRegister("a0",0x62fd7000L);e.writeRegister(e.getPCRegister(),e.readRegister("ra"));continue;}
                    if(pc==0xa00ee8fcL)crcCalls++;
                    if(pc==0xa000589cL||pc==0xa00501beL){
                        JsonObject call=new JsonObject();call.addProperty("pc",Long.toHexString(pc));for(String n:new String[]{"a0","a1","a2"})call.addProperty(n,e.readRegister(n).longValue());calls.add(call);
                        if(pc==0xa000589cL){if(!entered)parserCopy=e.readRegister("a2").intValue();else{handlerCopies++;destination=e.readRegister("a0").longValue();}}
                        if(entered&&pc==0xa00501beL&&c[6]==5){endpoint=5;break;}
                    }
                    if(pc==0xa008b51aL||pc==0xa00a389cL||pc==0xa01b2804L){e.writeRegister(e.getPCRegister(),e.readRegister("ra"));continue;}
                    if(!e.step(monitor))throw new AssertionError("case="+index+" pc="+Long.toHexString(pc)+" "+e.getLastError());
                }
                if(!entered||endpoint!=c[6]||crcCalls!=1||parserCopy!=c[1]+2||cursor!=wire.length)throw new AssertionError("case="+index+" endpoint="+endpoint+" crc="+crcCalls+" copy="+parserCopy);
                if(row.get("callback_cmd").getAsInt()!=c[0]||row.get("callback_length").getAsInt()!=c[1])throw new AssertionError("Callback mismatch");
                if(c[6]==5){int expected=c[0]==0xd1?7:c[0]==0x55?24:c[0]==0x57?6:c[0]==0x58?4:3;
                    if(e.readRegister("a1").signum()!=0||e.readRegister("a2").intValue()!=expected)throw new AssertionError("NULL comparison mismatch");}
                if(c[6]==1&&e.readRegister("a2").signum()!=0)throw new AssertionError("Expected NULL");
                int expectedCopies=c[0]==0x56&&c[1]==13?1:0;
                if(handlerCopies!=expectedCopies||(expectedCopies!=0&&destination!=(c[5]!=0&&c[3]==0?0x62fd1018L:0)))throw new AssertionError("Handler copy mismatch");
                row.addProperty("case",index);row.add("input",new Gson().toJsonTree(c));row.addProperty("wire_hex",HexFormat.of().formatHex(wire));row.addProperty("steps",steps);
                row.addProperty("endpoint",endpoint);row.addProperty("stop_pc",e.readRegister(e.getPCRegister()).toString(16));row.addProperty("crc_calls",crcCalls);
                row.addProperty("parser_copy_bytes",parserCopy);row.addProperty("handler_copies",handlerCopies);if(handlerCopies>0)row.addProperty("handler_destination",Long.toHexString(destination));
                row.addProperty("transport_state",e.readMemory(toAddr(0x62fcb2f0L),1)[0]&255);row.add("memory_calls",calls);rows.add(row);
            } finally {e.dispose();}
        }
        JsonObject out=new JsonObject();out.addProperty("rom_sha256",sha);out.addProperty("language",currentProgram.getLanguageID().toString());out.addProperty("passed",true);
        out.addProperty("scope","Original parser, CRC, copies and ordinary response dispatcher connected. Synthetic UART read/errno/RAM, writable zero page; passive log/notification/scheduler fixtures. Stops before declared hazardous read/comparison or when first callback returns to parser. No device access or full lifecycle execution.");out.add("cases",rows);
        Files.writeString(output,new GsonBuilder().setPrettyPrinting().create().toJson(out));println("AP01_UART_END_TO_END_REPLAY_PASS cases="+cases.length);
    }
}
