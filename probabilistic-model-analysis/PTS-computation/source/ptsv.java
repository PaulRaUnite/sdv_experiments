import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

class Trans {
    int src;
    String lbl;
    int time;
    int ctr;
    double prb;
    int dst;
    public Trans(int src, String lbl, int tm, int dst) {
        this.src = src;
        this.lbl = lbl;
        this.time = tm;
        this.ctr = 0;
        this.prb = 1.0;
        this.dst = dst;
    }
    public Trans(int src, String lbl, int tm, int dst, int ctr, double prb) {
        this.src = src;
        this.lbl = lbl;
        this.time = tm;
        this.ctr = ctr;
        this.prb = prb;
        this.dst = dst;
    }
    public void ctrUp () {
        ctr++;
    }
    public void prbComp(int ctrState) {
        prb = (double) ctr / ctrState;
    }
}

public class ptsv {
    public static void main(String[] args) throws IOException {
        // long startTime = System.currentTimeMillis();
        String fileLTS = args[0];
        String fileRemLTS = fileLTS + "-rem";
        String propRemMeta = "";
        String dirTrace = args[1];
        String fileTrace = dirTrace + "/T1" + ".txt";
        int numTrace = Integer.parseInt(args[2]);
        String propMeta = "";
        int tmpSrc;
        String tmpLbl = "";
        String tmpLblAct = "";
        int tmpLblTime = 0;
        int tmpDst;
        Set <Trans> tmpTrans;
        String[] arrLines;
        Map <Integer, Set <Trans>> inLTS = new HashMap <Integer, Set <Trans>>();
        Map <Integer, Set <Trans>> cutLTS = new HashMap <Integer, Set <Trans>>();
        Map <Integer, Set <Trans>> cutLTSRenum = new HashMap <Integer, Set <Trans>>();
        Map <Integer, Integer> mapCtr = new HashMap <Integer, Integer>();
        try(BufferedReader br = new BufferedReader(new FileReader(fileLTS + ".aut"))) {
            String line = br.readLine();
            propMeta = line;
            while (true) {
                line = br.readLine();
                if (line != null){
                    arrLines = line.replace(" ", "").replace("(", "").replace(")", "").replace("\"", "").split(",");
                    tmpSrc = Integer.parseInt(arrLines[0]);
                    tmpLbl = arrLines[1];
                    tmpDst = Integer.parseInt(arrLines[2]);

                    tmpTrans = new HashSet<Trans>();  
                    if (inLTS.containsKey(tmpSrc)) {
                        tmpTrans.addAll(inLTS.get(tmpSrc));
                    }
                    tmpLblAct = tmpLbl.split("_")[0];
                    if (tmpLblAct.equals("Time")) {
                        tmpLblTime = Integer.parseInt(tmpLbl.split("_")[1]);
                        tmpLbl = tmpLbl.split("_")[0];
                    } else {
                        tmpLblTime = 0;
                    }
                    tmpTrans.add(new Trans(tmpSrc, tmpLbl, tmpLblTime, tmpDst));
                    inLTS.put(tmpSrc, tmpTrans);

                    if(!inLTS.containsKey(tmpDst)) {
                        inLTS.put(tmpDst, new HashSet<Trans>());
                    }
                } else { break; }
            }
        }
        for (int stmap : inLTS.keySet()) {
            mapCtr.put(stmap, 0);
        }
        
        boolean firstCompute = true;
        System.out.println("computing: " + dirTrace + "/T" + 1 + ".txt");
        computePTS(inLTS, mapCtr, fileTrace, firstCompute);
        firstCompute = false;
        for (int t = 2; t <= numTrace; t++) {
            String traceNow = dirTrace + "/T" + t + ".txt";
            System.out.println("computing: " + dirTrace + "/T" + t + ".txt");
            computePTS(inLTS, mapCtr, traceNow, firstCompute);
        }

        for (int st : inLTS.keySet()) {
            for (Trans trs : inLTS.get(st)) {
                trs.prbComp(mapCtr.get(st));
            }
        }

        int tmpTrCtr = 0;
        double tmpProb = 0.0;
        for (int state : inLTS.keySet()) {
            tmpTrCtr = 0;
            tmpProb = 0.0;
            for (Trans tr : inLTS.get(state)) {
                tmpTrCtr += tr.ctr;
                tmpProb += tr.prb;
            }
            if (tmpTrCtr == 0) {
                for (Trans tr : inLTS.get(state)) {
                    tr.prb = (double) 1 / inLTS.get(state).size();
                }
            }
            if (tmpProb < 1) {
                for (Trans tr : inLTS.get(state)) {
                    tr.prb = (double) tr.prb / tmpProb;
                }
            }
        }

        removeTrans(inLTS, cutLTS);
        renumStates(cutLTS, cutLTSRenum);
        propRemMeta = computeMeta(cutLTSRenum);
        writePTS(inLTS, fileLTS, propMeta);
        writePTS(cutLTSRenum, fileRemLTS, propRemMeta);
        // long stopTime = System.currentTimeMillis();
        // long elapsedTime = stopTime - startTime;
        // System.out.println(elapsedTime);
    }

    public static void renumStates (Map<Integer, Set<Trans>> cutLTS, Map<Integer, Set<Trans>> renumLTS) {
        int numStates = 0;
        Map <Integer, Integer> mapRenum = new HashMap <Integer, Integer>();
        for (int st : cutLTS.keySet()) {
            mapRenum.put(st, numStates);
            numStates++;
        }

        Set <Trans> tmpTrans;
        for (int st : cutLTS.keySet()) {
            for (Trans tr : cutLTS.get(st)) {
                int newSrc = mapRenum.get(st);
                int newDst = mapRenum.get(tr.dst);
                tmpTrans = new HashSet<Trans>();  
                if (renumLTS.containsKey(newSrc)) {
                    tmpTrans.addAll(renumLTS.get(newSrc));
                }
                tmpTrans.add(new Trans(newSrc, tr.lbl, tr.time, newDst, tr.ctr, tr.prb));
                renumLTS.put(newSrc, tmpTrans);

                if(!renumLTS.containsKey(newDst)) {
                    renumLTS.put(newDst, new HashSet<Trans>());
                }
            }
        }
    }

    public static String computeMeta (Map<Integer, Set<Trans>> cutLTS) {
        String meta = "";
        int source = 0;
        int numTrans = 0;
        int numStates = 0;
        for (int st : cutLTS.keySet()) {
            numStates++;
            for (Trans tr : cutLTS.get(st)) {
                numTrans++;
            }
        }
        meta = "des (" + source + ", " + numTrans + ", " + numStates + ")";
        return meta;
    }
    public static void removeTrans (Map<Integer, Set<Trans>> inLTS, Map<Integer, Set<Trans>> cutLTS) {
        Set <Trans> tmpTrans;
        for (int st : inLTS.keySet()) {
            for (Trans tr : inLTS.get(st)) {
                if (tr.ctr > 0) {
                    tmpTrans = new HashSet<Trans>();  
                    if (cutLTS.containsKey(st)) {
                        tmpTrans.addAll(cutLTS.get(st));
                    }
                    tmpTrans.add(new Trans(tr.src, tr.lbl, tr.time, tr.dst, tr.ctr, tr.prb));
                    cutLTS.put(st, tmpTrans);

                    if(!cutLTS.containsKey(tr.dst)) {
                        cutLTS.put(tr.dst, new HashSet<Trans>());
                    }
                }
            }
        }
    }

    public static void printLTS (Map<Integer, Set<Trans>> inLTS) {
        for (int st : inLTS.keySet()) {
            System.out.println("State " + st);
            for (Trans tr : inLTS.get(st)) {
                System.out.print("\tSrc: " + tr.src + ", Lbl: " + tr.lbl + ", Tgt: " + tr.dst);
                System.out.println();
            }
        }
    }

    public static void findTimeTrace(Map<Integer, Set<Trans>> inLTS, int cState, String action, int timeGoal, int timeNow, ArrayList <String> timeTrace) {
        for (Trans tr : inLTS.get(cState)) {
            if (tr.lbl.equals("Time")) {
                if ((timeNow + tr.time) <= timeGoal) {
                    timeNow += tr.time;
                    cState = tr.dst;
                    timeTrace.add("T" + tr.time);
                    findTimeTrace(inLTS, cState, action, timeGoal, timeNow, timeTrace);
                    if (!timeTrace.get(timeTrace.size() - 1).equals(action)) {
                        timeTrace.remove(timeTrace.size() - 1);
                        timeNow -= tr.time;
                    }
                }
            } else if (tr.lbl.equals(action) && timeGoal == timeNow) {
                timeTrace.add(action);
            }
        }
    }

    public static void computePTS (Map<Integer, Set<Trans>> inLTS, Map<Integer, Integer> mapCtr, String fileTrace, boolean firstCompute) throws IOException {
        BufferedReader brTest = new BufferedReader(new FileReader(fileTrace));
        String [] trace = brTest.readLine().replace("'", "").split(",");
        int cState = 0;
        if (firstCompute) {
            mapCtr.put(cState, 1);
        } else {
            int initStateCtr = mapCtr.get(cState) + 1;
            mapCtr.put(cState, initStateCtr);
        }
        
        boolean isFound = false;
        boolean isNotified = false;
        int tmpCState = cState;
        for (String actx : trace) {
            String act = actx.split(" ")[0];
            int timeInt = 0;
            if (actx.split(" ").length > 1) {
                String time = actx.split(" ")[1];
                timeInt = Integer.parseInt(time);
            }
            if (timeInt == 0) {
                tmpCState = cState;
                isFound = false;
                inner:
                for (Trans trs : inLTS.get(cState)) {
                    if (trs.lbl.equals(act)) {
                        isFound = true;
                        trs.ctrUp();
                        cState = trs.dst;
                        mapCtr.put(cState, mapCtr.get(cState) + 1);
                        break inner;
                    }
                }
                if (isFound == false && isNotified == false) {
                    isNotified = true;
                    System.out.println("No trans in state " + tmpCState + " is labelled with " + act);
                }
            } else {
                ArrayList <String> timeTrace = new ArrayList<>();
                int timeNow = 0;
                String timeT = "";
                findTimeTrace(inLTS, cState, act, timeInt, timeNow, timeTrace);
                
                if (timeTrace.get(timeTrace.size() - 1).equals(act)) {
                    int idxTillLast = 0;
                    int last = timeTrace.size();
                    for (String timeAct : timeTrace) {
                        idxTillLast++;
                        inner:
                        for (Trans trs : inLTS.get(cState)) {
                            timeT = "T" + trs.time;
                            if (timeT.equals(timeAct) || (trs.lbl.equals(timeAct) && idxTillLast == last)) {
                                trs.ctrUp();
                                cState = trs.dst;
                                mapCtr.put(cState, mapCtr.get(cState) + 1);
                                break inner;
                            }
                        }
                    }
                } else if (isNotified == false) {
                    isNotified = true;
                    System.out.println("Time on the trace does not match with total time on the transitions from state " + cState);
                }
            }
        }
    }

    public static void printPTS (Map<Integer, Set<Trans>> inLTS, Map <Integer, Integer> mapCtr) {
        DecimalFormat df = new DecimalFormat();
        df.setMaximumFractionDigits(2);
        String tmpTime = "";
        System.out.println();
        for (int st : inLTS.keySet()) {
            System.out.println();
            System.out.println("State: " + st + ", Ctr: " + mapCtr.get(st));
            for (Trans itrs : inLTS.get(st)) {
                tmpTime = "";
                if (itrs.time > 0) {
                    tmpTime = "_" + itrs.time;
                }
                System.out.println("\tSrc: " + itrs.src + ", Lbl: "+ itrs.lbl + tmpTime
                + ", Ctr: " + itrs.ctr + ", Dst: " + itrs.dst + ", Prb: " + df.format(itrs.prb));
            }
        }
    }

    public static void writePTS (Map<Integer, Set<Trans>> inLTS, String fileName, String fileHeader) {
        try {
            FileWriter myWriter = new FileWriter(fileName + "-pts"+".aut");
            myWriter.write(fileHeader+"\n");
            String tmpTime = "";
            DecimalFormat df = new DecimalFormat();
            df.setMaximumFractionDigits(8);
            for (int st : inLTS.keySet()) {
                for (Trans itrs : inLTS.get(st)) {
                    tmpTime = "";
                    if (itrs.time > 0) {
                        tmpTime = "_" + itrs.time;
                    }
                    myWriter.write("(" + st + ", \"" + itrs.lbl + tmpTime + "; prob " + df.format(itrs.prb)
                        + "\", " + itrs.dst + ")\n");
                }
            }
            myWriter.close();
            System.out.println("PTS created: " + fileName + "-pts"+".aut");
        } catch (IOException e) {
            System.out.println("PTS computation error!");
            e.printStackTrace();
        }
    }
}