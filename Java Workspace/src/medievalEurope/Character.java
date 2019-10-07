package medievalEurope;

import java.util.*;

public class Character {

	private String name;
	private String nickname;
	private int ID = 0;
	
	private static ArrayList<Character> charList = medievalEurope.MedievalEurope.charList;
	
	private static int count = 0;
	
	private Character father;
	private Character mother;
	
	private ArrayList<Relation> relations = new ArrayList<Relation>();
	private ArrayList<Character> spouses = new ArrayList<Character>();
	private ArrayList<Character> children = new ArrayList<Character>();
	private ArrayList<Title> titles = new ArrayList<Title>();
	
	final static int FEMALE = -1;
	final static int MALE = 1;
	private int gender;
	
	private String birthday;
	private String deathday;
	
	public Character() {
		
	}
	public Character(String name, int gender) {
		this.name = name;
		this.gender = gender;
		
		ID = count++;
	}
	
	public void setRelation(Relation r) {
		if(r.getType() == Relation.CHILD)
			addChild(charList.get(r.getTarget()));
		else if(r.getType() == Relation.MOTHER)
			setMother(charList.get(r.getTarget()));
		else if(r.getType() == Relation.FATHER)
			setFather(charList.get(r.getTarget()));
		else if(r.getType() == Relation.SPOUSE)
			addSpouse(charList.get(r.getTarget()));
	}
	public void addRelation(Relation r) {
		relations.add(r);
	}
	public ArrayList<Relation> getRelations() {
		return relations;
	}
	
	public boolean setGender(int g) {
		if(g == FEMALE || g == MALE) {
			gender = g;
			return true;
		}
		else
			return false;
	}
	public String getGender() {
		if(gender == MALE)
			return "Male";
		else
			return "Female";
	}
	public int getGenderInt() {
		return gender;
	}
	
	public void setBirthday(String bday) {
		birthday = bday;
	}
	public String getBirthday() {
		return birthday;
	}
	public void setDeathday(String dday) {
		deathday = dday;
	}
	public String getDeathday() {
		return deathday;
	}
	public void setName(String nm) {
		name = nm;
	}
	public String getName() {
		return name;
	}
	public void setMother(Character mom) {
		mother = mom;
	}
	public Character getMother() {
		return mother;
	}
	public void setFather(Character dad) {
		father = dad;
	}
	public Character getFather() {
		return father;
	}
	public String getMotherName() {
		if(mother == null)
			return "";
		else
			return mother.getName();
	}
	public String getFatherName() {
		if(father == null)
			return "";
		else
			return father.getName();
	}
	
	public void addSpouse(Character spouse) {
		if(spouses.size() == 0 || spouses.get(0) != null)
			spouses.add(spouse);
		else
			spouses.set(0, spouse);
	}
	public ArrayList<Character> getSpouses() {
		return spouses;
	}
	public boolean isSpouse(int id) {
		if(spouses.get(0) == null)
			return false;
		else {
			for(int i = 0; i < spouses.size(); i++) {
				Character c = spouses.get(i);
				if(c.getID() == id) {
					return true;
				}
			}
			return false;
		}
	}
	public Character removeSpouse(int id) {
		if(spouses.get(0) == null)
			return null;
		else {
			for(int i = 0; i < spouses.size(); i++) {
				Character c = spouses.get(i);
				if(c.getID() == id) {
					spouses.remove(i);
					return c;
				}
			}
			
			return null;
		}
	}
	
	public void addChild(Character child) {
		if(children.size() == 0 || children.get(0) != null)
			children.add(child);
		else
			children.set(0, child);
	}
	public ArrayList<Character> getChildren() {
		return children;
	}
	public boolean isChild(int id) {
		if(children.get(0) == null)
			return false;
		else {
			for(int i = 0; i < children.size(); i++) {
				Character c = children.get(i);
				if(c.getID() == id) {
					return true;
				}
			}
			return false;
		}
	}
	public Character removeChild(int id) {
		if(children.get(0) == null)
			return null;
		else {
			for(int i = 0; i < children.size(); i++) {
				Character c = children.get(i);
				if(c.getID() == id) {
					children.remove(i);
					return c;
				}
			}
			
			return null;
		}
	}
	
	public void addTitle(Title t) {
		titles.add(t);
	}
	public ArrayList<Title> getTitles() {
		return titles;
	}
	
	public void setNickName(String n) {
		nickname = n;
	}
	public String getNickName() {
		return nickname;
	}
	
	public void setID(int id) {
		ID = id;
	}
	public int getID() {
		return ID;
	}
	
	public String toString() {
		return ID + ": " + name;
	}
}
