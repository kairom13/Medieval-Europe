package medievalEurope;

import java.time.*;
import java.util.ArrayList;

public class Title {
	private int ID;
	private static int count = 0;
	
	private String name;
	
	private LocalDate startDate;
	private LocalDate endDate;
	
	private Character ruler;
	private Fief fief;
	
	private Title predecessor = null;
	private Title successor = null;
	
	private ArrayList<Relation> relations = new ArrayList<Relation>();
	
	public Title() {
		
	}
	public Title(LocalDate startDate, Fief fief, Character ruler, LocalDate endDate) {
		ID = count++;
		
		this.startDate = startDate;
		this.endDate = endDate;
		
		this.ruler = ruler;
		this.ruler.addTitle(this);
		
		this.fief = fief;
		this.fief.addTitle(this);
		
		setName();
	}
	public Title(Character ruler) {
		this.ruler = ruler;
		this.ruler.addTitle(this);
	}
	
	private void setName() {
		if(fief.getType() == Fief.COUNTY)
			name = "Count of " + fief.getName();
		else if(fief.getType() == Fief.DUCHY)
			name = "Duke of " + fief.getName();
		else if(fief.getType() == Fief.KINGDOM)
			name = "King of " + fief.getName();
		else if(fief.getType() == Fief.EMPIRE)
			name = "Emperor of " + fief.getName();
		else if(fief.getType() == Fief.MARGRAVIATE)
			name = "Margrave of " + fief.getName();
		else if(fief.getType() == Fief.BISHOPRIC)
			name = "Bishop of " + fief.getName();
		else if(fief.getType() == Fief.ARCHBISHOPRIC)
			name = "Archbishop of " + fief.getName();
	}
	public String getTitle() {
		return name;
	}
	
	public void addRelation(Relation r) {
		relations.add(r);
	}
	public ArrayList<Relation> getRelations() {
		return relations;
	}
	
	public void setPredecessor(Title pre) {
		predecessor = pre;
			
	}
	public Title getPredecessor() {
		return predecessor;
	}
	
	public void setSuccessor(Title suc) {
		successor = suc;
	}
	public Title getSuccessor() {
		return successor;
	}
	
	public Fief getFief() {
		return fief;
	}
	public Character getRuler() {
		return ruler;
	}
	
	public LocalDate getStart() {
		return startDate;
	}
	public LocalDate getEnd() {
		return endDate;
	}
	
	public int getID() { 
		return ID;
	}
}
