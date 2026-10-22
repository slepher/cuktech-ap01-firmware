// Controlled replay of original receive/CRC/copy instructions, never a device UART.
// @category AP01.Research
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import com.google.gson.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

public class Ap01UartReceiveReplay0041 extends GhidraScript {
    private static final String SHA="972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9";
    private void word(EmulatorHelper e,long a,long v) {byte[] b=new byte[4];for(int i=0;i<4;i++)b[i]=(byte)(v>>>(8*i));e.writeMemory(toAddr(a),b);}
    private void byteAt(EmulatorHelper e,long a,int v) {e.writeMemory(toAddr(a),new byte[]{(byte)v});}
    private int crc(byte[] data) {int c=0;for(byte v:data){c^=(v&255)<<8;for(int i=0;i<8;i++)c=((c<<1)^((c&0x8000)!=0?0x1021:0))&65535;}return c;}
    private byte[] frame(int declared,byte[] payload) {
        byte[] body=new byte[3+payload.length];body[1]=(byte)0xd0;body[2]=(byte)declared;System.arraycopy(payload,0,body,3,payload.length);
        int c=crc(body);ArrayList<Byte> out=new ArrayList<>();out.add((byte)0xa5);
        for(int i=0;i<body.length+2;i++){int v=i<body.length?body[i]&255:(i==body.length?c&255:c>>>8);if(v==0xa5||v==0x5a||v==0xaa)out.add((byte)0xaa);out.add((byte)v);}
        out.add((byte)0x5a);byte[] result=new byte[out.size()];for(int i=0;i<result.length;i++)result[i]=out.get(i);return result;
    }
    public void run() throws Exception {
        byte[] image=new byte[6769704];if(currentProgram.getMemory().getBytes(toAddr(0x9ffff000L),image)!=image.length ||
            !HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(image)).equals(SHA))throw new IllegalArgumentException("Wrong original ROM");
        JsonArray rows=new JsonArray();
        int[] declarations={0,1,255};byte[][] payloads={new byte[0],new byte[]{0},new byte[0]};
        for(int index=0;index<declarations.length;index++) {
            byte[] wire=frame(declarations[index],payloads[index]);EmulatorHelper e=new EmulatorHelper(currentProgram);
            int cursor=0,steps=0,copy=-1,crcCalls=0;boolean reached=false;JsonObject row=new JsonObject();
            try {
                for(String n:"zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5 a6 a7 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 t3 t4 t5 t6".split(" "))e.writeRegister(n,0);
                // RAM is a synthetic, private emulator state. Source canaries expose reads beyond the received frame.
                byte[] ram=new byte[0x10000];Arrays.fill(ram,(byte)0);e.writeMemory(toAddr(0x62fc0000L),ram);
                byte[] source=new byte[0x110];Arrays.fill(source,(byte)0xa6);e.writeMemory(toAddr(0x62fcb458L),source);
                byteAt(e,0x62fcb487L,0);byteAt(e,0x62fcb488L,0);byteAt(e,0x62fcb489L,0);
                byteAt(e,0x62fcb420L,0x7e);byteAt(e,0x62fcb2f0L,2);byteAt(e,0x62fcb2f3L,0xd0);
                word(e,0x62fcb6c0L,0x1000);word(e,0x62fc91b0L,7);word(e,0x62fd7000L,11);
                e.writeRegister("sp",0x62fd8000L);e.writeRegister("ra",0x1004);e.writeRegister("a0",0);e.writeRegister("a1",0);e.writeRegister("a2",1);
                e.writeRegister(e.getPCRegister(),0xa00a8330L);
                while(steps++<30000) {
                    monitor.checkCancelled();long pc=e.readRegister(e.getPCRegister()).longValue();
                    if(pc==0x1000) {reached=true;row.addProperty("callback_cmd",e.readRegister("a0").intValue());row.addProperty("callback_declared_length",e.readRegister("a1").intValue());break;}
                    if(pc==0x1004)break;
                    if(pc==0xa003f6a2L) {
                        if(e.readRegister("a0").intValue()!=7 || e.readRegister("a2").intValue()!=1)throw new AssertionError("Unexpected read API");
                        if(cursor<wire.length){byteAt(e,e.readRegister("a1").longValue(),wire[cursor++]&255);e.writeRegister("a0",1);}
                        else e.writeRegister("a0",0xffffffffL);
                        e.writeRegister(e.getPCRegister(),e.readRegister("ra"));continue;
                    }
                    if(pc==0xa00267c0L){e.writeRegister("a0",0x62fd7000L);e.writeRegister(e.getPCRegister(),e.readRegister("ra"));continue;}
                    if(pc==0xa000589cL)copy=e.readRegister("a2").intValue();
                    if(pc==0xa00ee8fcL)crcCalls++;
                    if(!e.step(monitor))throw new AssertionError("pc="+Long.toHexString(pc)+" "+e.getLastError());
                }
                int marker=e.readMemory(toAddr(0x62fcb420L),1)[0]&255;
                if(!reached || copy!=declarations[index]+2 || crcCalls!=1 || (index<2?marker!=0x7e:marker!=0xa6))throw new AssertionError("Receive contract mismatch at case "+index+" copy="+copy+" marker="+marker);
                row.addProperty("case",index);row.addProperty("wire_hex",HexFormat.of().formatHex(wire));row.addProperty("steps",steps);
                row.addProperty("actual_payload_bytes",payloads[index].length);row.addProperty("original_memcpy_length",copy);
                row.addProperty("crc_helper_executions",crcCalls);row.addProperty("ota_error_canary_before",0x7e);row.addProperty("ota_error_canary_after",marker);rows.add(row);
            } finally {e.dispose();}
        }
        JsonObject out=new JsonObject();out.addProperty("rom_sha256",SHA);out.addProperty("language",currentProgram.getLanguageID().toString());out.addProperty("passed",true);
        out.addProperty("scope","Original UART parser, CRC helper and memcpy instructions; synthetic byte-read/errno fixtures; stop before passive response callback. No device/network/full-ROM execution.");out.add("cases",rows);
        Files.writeString(Path.of(getScriptArgs()[0]),new GsonBuilder().setPrettyPrinting().create().toJson(out));println("AP01_UART_RECEIVE_REPLAY_PASS cases="+declarations.length);
    }
}
