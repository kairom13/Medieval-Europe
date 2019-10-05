package medievalEurope;

import java.util.*;

public class Fief {
	
	private int ID;
	private String name;
	private int type;
	
	private static int count = 0;
	
	public final static int COUNTY = 0;
	public final static int DUCHY = 1;
	public final static int KINGDOM = 2;
	public final static int EMPIRE = 3;
	public final static int MARGRAVIATE = 4;
	public final static int BISHOPRIC = 5;
	public final static int ARCHBISHOPRIC = 6;
	
	private ArrayList<Character> rulers;

	public Fief(int ID, String name, int type) {
		this.name = name;
		this.type = type;
		this.ID = ID;
	}
	
}