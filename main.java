import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.text.DecimalFormat;
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.JButton;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JTextArea;
import java.io.FileWriter;
import java.io.IOException;

public class main extends JPanel {
    private JTextArea jcomp1;
    private JTextArea jcomp2;
    private JButton jcomp3;
    private JButton jcomp4;
    private JButton jcomp5;
    private JButton jcomp6;
    private JLabel jcomp7;
    private JLabel jcomp8;
    private JLabel jcomp9;
    private JMenuBar jcomp10;
    private JTextField jcomp11;
    private JLabel jcomp12;
    private JComboBox jcomp13;
    private JLabel jcomp14;
    private JButton jcomp15;
    private JLabel jcomp16;


    public main() {

        JMenu fileMenu = new JMenu("File");
        JMenuItem exitItem = new JMenuItem("Exit");


        fileMenu.add(exitItem);
        JMenu helpMenu = new JMenu("Help");
        JMenuItem contentsItem = new JMenuItem("Contents");
        helpMenu.add(contentsItem);
        JMenuItem aboutItem = new JMenuItem("About");
        helpMenu.add(aboutItem);

        jcomp1 = new JTextArea(5, 5);
        // jcomp1.setMargin(new Insets(5, 5, 5, 5));
        JScrollPane scrollPane = new JScrollPane(jcomp1);
        scrollPane.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
        
        jcomp2 = new JTextArea(5, 5);
        JScrollPane scroll;
        scroll = new JScrollPane(jcomp1, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED, JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED);
        // this.setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5));
        jcomp3 = new JButton("Select File");
        
        jcomp4 = new JButton("Paraphrase");
        jcomp5 = new JButton("Copy Text");
        jcomp6 = new JButton("Rephrase");
        jcomp7 = new JLabel("Original Text");
        jcomp8 = new JLabel("Generated Text");
        jcomp9 = new JLabel("Paraphrasing Tool");
        jcomp10 = new JMenuBar();
        jcomp10.add(fileMenu);
        jcomp10.add(helpMenu);
        jcomp11 = new JTextField(5);
        jcomp12 = new JLabel("Similarity");
        jcomp13 = new JComboBox();
        jcomp13.addItem("Select");
        jcomp13.addItem("Save to File");
        jcomp14 = new JLabel("Action");
        jcomp15 = new JButton("OK");
        jcomp16 = new JLabel("");
        JFileChooser fc = new JFileChooser();
        JFrame frame = new JFrame();
        jcomp3.addActionListener(ev -> {
            int returnVal = fc.showOpenDialog(frame);
            if (returnVal == JFileChooser.APPROVE_OPTION) {
                File file = fc.getSelectedFile();
                try {
                    BufferedReader input = new BufferedReader(new InputStreamReader(
                        new FileInputStream(file)));
                    jcomp1.read(input, "READING FILE :-)");
                } catch (Exception e) {
                    e.printStackTrace();
                }
            } else {
                System.out.println("Operation is CANCELLED :(");
            }
        });

        jcomp5.addActionListener(ev -> {
            jcomp2.selectAll();
            jcomp2.copy();
        });
        exitItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent event) {
                System.exit(0);
            }

        });

        jcomp4.addActionListener(ev -> {
            jcomp1.selectAll();
            String text = jcomp1.getText();

            String input = "python3 helpers.py "  + text ;

            String s = null;

            try {
                System.out.println(input);
                Process p = Runtime.getRuntime().exec(input);

                BufferedReader stdInput = new BufferedReader(new InputStreamReader(p.getInputStream()));

                while ((s = stdInput.readLine()) != null) {
                   jcomp2.setText(s);
                    double sim = StringEquality.similarity(s, text);
                    String sim2=sim+" %";
                    // System.out.print(sim2);
                    jcomp11.setText(sim2);

                }

                // StringEquality eq=new StringEquality();
                
            } catch (IOException e) {
                jcomp2.setText("exception happened - here's what I know: ");
                e.printStackTrace();
            }
        });


        exitItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent event) {
                System.exit(0);
            }

        });

        jcomp15.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent event) {

                Object selected = jcomp13.getSelectedItem();
                if (selected.toString().equals("Select"))
                    jcomp16.setText("Select a option");
                else if (selected.toString().equals("Save to File")) {
                    int returnVal = fc.showOpenDialog(frame);
                    if (returnVal == JFileChooser.APPROVE_OPTION) {
                        File file = fc.getSelectedFile();
                        try {
                            FileWriter fileWriter = new FileWriter(file);
                            jcomp2.write(fileWriter);
                            fileWriter.close();
                            jcomp16.setText("written");
                        } catch (Exception e) {
                            //TODO: handle exception
                        }
                    }
                }
            }
        });

       
        //adjust size and set layout
        // setPreferredSize(new Dimension(944, 574));
        setPreferredSize (new Dimension (1366, 721));
        setLayout(null);

        //add components
        add(jcomp1, BorderLayout.CENTER);
        add(scrollPane);
        // add(sp);
        add(jcomp2);
        add(jcomp3);
        add(jcomp4);
        add(jcomp5);
        add(jcomp6);
        add(jcomp7);
        add(jcomp8);
        add(jcomp9);
        add(jcomp10);
        add(jcomp11);
        add(jcomp12);
        add(jcomp13);
        add(jcomp14);
        add(jcomp15);
        add(jcomp16);

        //set component bounds (only needed by Absolute Positioning)
        jcomp1.setBounds(110, 165, 330, 300);
        scroll.setBounds(110, 165, 330, 300);
        jcomp2.setBounds(475, 165, 335, 305);
        jcomp3.setBounds(115, 480, 130, 25);
        jcomp4.setBounds(295, 480, 135, 25);
        jcomp5.setBounds(490, 480, 130, 25);
        jcomp6.setBounds(675, 480, 120, 25);
        jcomp7.setBounds(110, 135, 100, 25);
        jcomp8.setBounds(475, 140, 110, 25);
        jcomp9.setBounds(200, 45, 525, 35);
        jcomp10.setBounds(0, 0, 1366, 30);
        jcomp11.setBounds(815, 205, 100, 25);
        jcomp12.setBounds(815, 175, 100, 25);
        jcomp13.setBounds(820, 285, 100, 25);
        jcomp14.setBounds(820, 250, 100, 25);
        jcomp15.setBounds(820, 325, 100, 25);
        jcomp16.setBounds(820, 360, 100, 25);
        jcomp1.setLineWrap(true);
        jcomp2.setLineWrap(true);
        jcomp1.setWrapStyleWord(true);
        jcomp2.setWrapStyleWord(true);
    }


    public static void main(String[] args) {

        JFrame frame = new JFrame("Paraphrasing Tool");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.getContentPane().add(new main());
        // frame.getContentPane().add(new main(), BorderLayout.CENTER);
        frame.pack();
        frame.setVisible(true);
    }
}

class StringEquality {


    // public static void printSimilarity(String s, String t) {
    //     System.out.println(String.format("%.3f is the similarity between \"%s\" and \"%s\"", similarity(s, t), s, t));
    // }
        // static final DecimalFormat df = new DecimalFormat("0.00");
    public static double similarity(String s1, String s2) {
        String longer = s1, shorter = s2;
        if (s1.length() < s2.length()) {
            longer = s2;
            shorter = s1;
        }
        int longerLength = longer.length();
        if (longerLength == 0) {
            return 1.0; /* both strings have zero length */
        }
        double sim = (longerLength - getLevenshteinDistance(longer, shorter)) / (double) longerLength;
        // BigDecimal sim3=new BigDecimal(sim);
        // BigDecimal sim2=sim3.setScale(2,RoundingMode.HALF_DOWN);
        // sim2=Float.parseFloat(s)
        sim=sim*100;
        sim=Math.ceil(sim);
        return sim;
    }

   
    public static int getLevenshteinDistance(String s, String t) {
        if (s == null || t == null) {
            throw new IllegalArgumentException("Strings must not be null");
        }

        int n = s.length(); // length of s
        int m = t.length(); // length of t

        if (n == 0) {
            return m;
        } else if (m == 0) {
            return n;
        }

        if (n > m) {
            // swap the input strings to consume less memory
            String tmp = s;
            s = t;
            t = tmp;
            n = m;
            m = t.length();
        }

        int p[] = new int[n + 1]; //'previous' cost array, horizontally
        int d[] = new int[n + 1]; // cost array, horizontally
        int _d[]; //placeholder to assist in swapping p and d

        // indexes into strings s and t
        int i; // iterates through s
        int j; // iterates through t

        char t_j; // jth character of t

        int cost; // cost

        for (i = 0; i <= n; i++) {
            p[i] = i;
        }

        for (j = 1; j <= m; j++) {
            t_j = t.charAt(j - 1);
            d[0] = j;

            for (i = 1; i <= n; i++) {
                cost = s.charAt(i - 1) == t_j ? 0 : 1;
                // minimum of cell to the left+1, to the top+1, diagonally left and up +cost
                d[i] = Math.min(Math.min(d[i - 1] + 1, p[i] + 1), p[i - 1] + cost);
            }

            // copy current distance counts to 'previous row' distance counts
            _d = p;
            p = d;
            d = _d;
        }

        // our last action in the above loop was to switch d and p, so p now 
        // actually has the most recent cost counts
        return p[n];
    }
}