package medievalEurope;

import java.util.ArrayList;

/**
 * Designates the relationship between two characters or titles, using their ids
 * 
 * Used as temporary storage of relationships until all characters/titles are initialized
 * @author kairom13
 *
 */
public class Relation {
	private ArrayList<Character> charList = medievalEurope.MedievalEurope.charList;

	//Character Relationships
	final static int MOTHER = 0;
	final static int FATHER = 1;
	final static int CHILD = 2;
	final static int SPOUSE = 3;
	
	//Title Relationships
	final static int PREDECESSOR = 4;
	final static int SUCCESSOR = 5;
	
	private int self;
	private int target;
	private int type;
	
	public Relation(int self, int target, int type) {
		this.self = self;
		this.target = target;
		this.type = type;
	}
	
	public int getTarget() {
		return target;
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
		else if(type == PREDECESSOR)
			t = SUCCESSOR;
		else if(type == SUCCESSOR)
			t = PREDECESSOR;
		else
			t = type;
		
		return new Relation(target, self, t);
	}
	public String toString() {
		return "Self ID: " + self + ", Target ID: " + target + ", Relationship: " + type;
	}
}
