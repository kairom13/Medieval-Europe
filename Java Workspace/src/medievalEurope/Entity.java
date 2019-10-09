package medievalEurope;

import java.time.LocalDate;
import java.util.ArrayList;

public class Entity {

	private int ID;
	private String name;
	
	private LocalDate startDate;
	private LocalDate endDate;
	
	private ArrayList<Relation> relations = new ArrayList<Relation>();
	
	public Entity() {
		
	}
	public Entity(int id, LocalDate start, LocalDate end) {
		ID = id;
		startDate = start;
		endDate = end;
	}
	public Entity(int id, String nm) {
		ID = id;
		name = nm;
	}
	public Entity(int id) {
		ID = id;
	}
	
	public void setName(String nm) {
		name = nm;
	}
	public String getName() {
		return name;
	}
	
	public void setStartDate(LocalDate start) {
		startDate = start;
	}
	public LocalDate getStartDate() {
		return startDate;
	}
	
	public void setEndDate(LocalDate end) {
		endDate = end;
	}
	public LocalDate getEndDate() {
		return endDate;
	}
	
	public void setID(int id) {
		ID = id;
	}
	public int getID() {
		return ID;
	}
	
	public void addRelation(Relation r) {
		relations.add(r);
	}
	public ArrayList<Relation> getRelations() {
		return relations;
	}
}
