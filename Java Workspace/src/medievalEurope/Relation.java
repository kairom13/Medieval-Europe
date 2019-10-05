package medievalEurope;

import java.util.ArrayList;

/**
 * Designates the relationship between two characters, using their ids
 * 
 * Used as temporary storage of relationships until all characters are initialized
 * @author kairom13
 *
 */
public class Relation {
	private ArrayList<Character> charList = medievalEurope.MedievalEurope.charList;

	final static int MOTHER = 0;
	final static int FATHER = 1;
	final static int CHILD = 2;
	final static int SPOUSE = 3;
	final static int TITLE = 4;
	
	private int self;
	private int relation;
	private int type;
	
	public Relation(int self, int relation, int type) {
		this.self = self;
		this.relation = relation;
		this.type = type;
	}
	
	public int getRelation() {
		return relation;
	}
	public int getType() {
		return type;
	}
	public int getSelf() {
		return self;
	}
	public Relation getInverse() {
		int t = -1;
		if(type == MOTHER || type == FATHER)
			t = CHILD;
		else if(type == CHILD) {
			if(charList.get(self).getGenderInt() == Character.MALE)
				t = FATHER;
			else
				t = MOTHER;
		}
		else
			t = type;
		return new Relation(relation, self, t);
	}
	public String toString() {
		return "Self ID: " + self + ", Target ID: " + relation + ", Relationship: " + type;
	}
}
