package medievalEurope;

import java.time.*;
import java.util.ArrayList;

public class Title extends Entity {
	private static int count = 0;

	private Character ruler;
	private Fief fief;
	
	private Title predecessor = null;
	private Title successor = null;
	
	private ArrayList<Relation> relations = new ArrayList<Relation>();
	
	public Title() {
		super();
	}
	public Title(LocalDate startDate, Fief fief, Character ruler, LocalDate endDate) {
		super(count++, startDate, endDate);
		
		this.ruler = ruler;		
		this.fief = fief;

		super.setName(setName());

		this.ruler.addTitle(this);
		this.fief.addTitle(this);
	}
	
	private String setName() {
		if(fief.getType() == Fief.COUNTY)
			return "Count of " + fief.getName();
		else if(fief.getType() == Fief.DUCHY)
			return "Duke of " + fief.getName();
		else if(fief.getType() == Fief.KINGDOM)
			return "King of " + fief.getName();
		else if(fief.getType() == Fief.EMPIRE)
			return "Emperor of " + fief.getName();
		else if(fief.getType() == Fief.MARGRAVIATE)
			return "Margrave of " + fief.getName();
		else if(fief.getType() == Fief.BISHOPRIC)
			return "Bishop of " + fief.getName();
		else if(fief.getType() == Fief.ARCHBISHOPRIC)
			return "Archbishop of " + fief.getName();
		else
			return null;
	}
	public String getTitle() {
		return super.getName();
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
	
	public boolean contains(Title t) {
		if(t.getStartDate().isBefore(super.getEndDate())) // The title begins in the middle of this title (means overlap)
			return true;
		else if(t.getEndDate().isAfter(super.getStartDate())) // The title ends in the middle of this title (means overlap)
			return true;
		else
			return false;
	}
}
