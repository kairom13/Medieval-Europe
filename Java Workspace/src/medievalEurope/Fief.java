package medievalEurope;

import java.time.LocalDate;
import java.util.*;

public class Fief {
	
	private int ID;
	private String name;
	private String fullName;
	private int type;
	
	private static int count = 0;
	
	public final static int COUNTY = 0;
	public final static int DUCHY = 1;
	public final static int KINGDOM = 2;
	public final static int EMPIRE = 3;
	public final static int MARGRAVIATE = 4;
	public final static int BISHOPRIC = 5;
	public final static int ARCHBISHOPRIC = 6;
	
	private ArrayList<Title> titles = new ArrayList<Title>();

	public Fief(int ID, String name, int type) {
		this.name = name;
		this.type = type;
		this.ID = ID;
		
		setFullName();
	}
	
	private void setFullName() {
		if(type == Fief.COUNTY)
			fullName = "County of " + name;
		else if(type == Fief.DUCHY)
			fullName = "Duchy of " + name;
		else if(type == Fief.KINGDOM)
			fullName = "Kingdom of " + name;
		else if(type == Fief.EMPIRE)
			fullName = "Empire of " + name;
		else if(type == Fief.MARGRAVIATE)
			fullName = "Margraviate of " + name;
		else if(type == Fief.BISHOPRIC)
			fullName = "Bishopric of " + name;
		else if(type == Fief.ARCHBISHOPRIC)
			fullName = "Archbishopric of " + name;
	}
	public void addTitle(Title t) {
		titles.add(t);
		//printTitles();
		//System.out.println("");
		titles = quicksort(titles);
		//printTitles();
		//System.out.println("-------------");
	}
	public String getName() {
		return name;
	}
	public String getFullName() {
		return fullName;
	}
	public int getType() {
		return type;
	}
	public int getID() {
		return ID;
	}
	public ArrayList<Title> getTitles() {
		return titles;
	}
	private void printTitles() {
		for(int i = 0; i < titles.size(); ++i) {
			Title t = titles.get(i);
			System.out.println(t.getTitle() + ": " + t.getStartDate() + " - " + t.getEndDate());
		}
	}
	private ArrayList<Title> quicksort(ArrayList<Title> input) {
		
		if(input.size() <= 1)
			return input;
		
		int middle = (int) Math.ceil((double)input.size() / 2);
		Title pivot = input.get(middle);

		ArrayList<Title> less = new ArrayList<Title>();
		ArrayList<Title> greater = new ArrayList<Title>();
		
		for (int i = 0; i < input.size(); i++) {
			if(i == middle)
				continue;
			else if(input.get(i).getEndDate().isBefore(pivot.getStartDate()))				
				less.add(input.get(i));
			else if(input.get(i).getStartDate().isAfter(pivot.getEndDate()))
				greater.add(input.get(i));
			else
				System.out.println("Title Overlap Error: " + input.get(i).getID() + ", " + pivot.getID());
		}
		
		return concatenate(quicksort(less), pivot, quicksort(greater));
	}
	private ArrayList<Title> concatenate(ArrayList<Title> less, Title pivot, ArrayList<Title> greater){
		ArrayList<Title> list = new ArrayList<Title>();
		
		for (int i = 0; i < less.size(); i++) 
			list.add(less.get(i));
		
		list.add(pivot);
		
		for (int i = 0; i < greater.size(); i++)
			list.add(greater.get(i));
		
		return list;
	}
	
}