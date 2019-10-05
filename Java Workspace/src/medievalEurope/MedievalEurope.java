package medievalEurope;

import java.awt.*;
import java.awt.event.*;
import java.util.*;
import javax.swing.*;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;

import java.io.*;
import java.text.SimpleDateFormat;
import java.time.LocalDate;
import java.time.Month;

public class MedievalEurope extends JFrame {
	
	final static int CHARACTER = 0;
	final static int FIEF = 1;
	
	final static int WIDTH = 800;
	final static int HEIGHT = 800;
	
	protected static ArrayList<Character> charList = new ArrayList<Character>();
	private static ArrayList<Fief> fiefList = new ArrayList<Fief>();
	
	static JPanel mainCards = new JPanel(new CardLayout());
	final static String NCHAR = "New Character Card";
	final static String MCARD = "Main Card";
	final static String CCHAR = "Choose Character Card";

	public static void main(String[] args) {
		MedievalEurope frame = new MedievalEurope();
		frame.setVisible(true);
	}
	public MedievalEurope() {
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setSize(WIDTH, HEIGHT);
		setResizable(false);
		
		Container pane = getContentPane();
		
		int startChar = 3;

		readData(CHARACTER);
		readData(FIEF);
		start(startChar, false, charList.get(startChar).getGenderInt());
		
		pane.add(mainCards, BorderLayout.CENTER);
	}
	public static void start(int id, boolean edit, int gender) {
		JPanel mainCard = new JPanel(null);
		
		Character person = charList.get(id);
	
		JButton editButton = new JButton("Edit");
		editButton.setBounds(WIDTH-60, 10, 50, 20);
		
		if(edit) {
			JTextField nmLabel = new JTextField(person.getName());
			nmLabel.setBounds(WIDTH/2 - 75, 10, 150, 20);
			
			JLabel bday = new JLabel("Birthday:");
			bday.setBounds(10, 70, 70, 20);
			
			JTextField bdayLabel = new JTextField(person.getBirthday());
			bdayLabel.setBounds(80, 70, 150, 20);
			
			JLabel dday = new JLabel("Deathday:");
			dday.setBounds(10, 100, 70, 20);
			
			JTextField ddayLabel = new JTextField(person.getDeathday());
			ddayLabel.setBounds(80, 100, 150, 20);

			JLabel genderLabel = new JLabel();
			genderLabel.setBounds(80, 40, 100, 20);
			if(gender == Character.FEMALE)
				genderLabel.setText("Gender: Female");
			else
				genderLabel.setText("Gender: Male");
			
			JButton switchGender = new JButton("Switch");
			switchGender.setBounds(10, 40, 60, 20);
			switchGender.addActionListener(new ActionListener() {

				@Override
				public void actionPerformed(ActionEvent e) {
					CardLayout cl = (CardLayout) (mainCards.getLayout());

					person.setBirthday(bdayLabel.getText());
					person.setDeathday(ddayLabel.getText());
					
					start(person.getID(), true, gender * -1);
					cl.show(mainCards, "Main Card");
				}
			});
			
			JLabel dadLabel = new JLabel("Father:");
			dadLabel.setBounds(80, 130, 60, 20);
			
			JLabel dadName = new JLabel(person.getFatherName());
			dadName.setBounds(140, 130, 150, 20);
			
			JButton addDad = new JButton("Add");
			addDad.setActionCommand(Integer.toString(Relation.FATHER));
			addDad.setBounds(10, 130, 60, 20);
			addDad.addActionListener(new ActionListener() {

				@Override
				public void actionPerformed(ActionEvent e) {	
					CardLayout cl = (CardLayout) (mainCards.getLayout());
					chooseCharacter(person, Relation.FATHER, null);
					cl.show(mainCards, "Choose Character Card");
				}
			});
			if(person.getFather() != null)
				addDad.setText("Change");

			mainCard.add(dadName);
			
			JLabel momLabel = new JLabel("Mother:");
			momLabel.setBounds(80, 160, 60, 20);
			
			JLabel momName = new JLabel(person.getMotherName());
			momName.setBounds(140, 160, 100, 20);
			
			JButton addMom = new JButton("Add");
			addMom.setBounds(10, 160, 60, 20);
			addMom.addActionListener(new ActionListener() {

				@Override
				public void actionPerformed(ActionEvent e) {
					CardLayout cl = (CardLayout) (mainCards.getLayout());
					chooseCharacter(person, Relation.MOTHER, null);
					cl.show(mainCards, "Choose Character Card");
				}
				
			});
			if(person.getMother() != null)
				addMom.setText("Change");
			
			mainCard.add(addMom);
			
			JLabel spouseLabel = new JLabel("Spouses:");
			spouseLabel.setBounds(80, 190, 80, 20);
			
			JButton addSpouse = new JButton("Add");
			addSpouse.setBounds(10, 190, 60, 20);
			addSpouse.addActionListener(new ActionListener() {

				@Override
				public void actionPerformed(ActionEvent e) {
					CardLayout cl = (CardLayout) (mainCards.getLayout());
					chooseCharacter(person, Relation.SPOUSE, null);
					cl.show(mainCards, "Choose Character Card");
				}
			});
			
			ArrayList<Character> spouses = person.getSpouses();
			for(int s = 0; s < spouses.size(); ++s) {
				Character spouse = spouses.get(s);
				if(spouse != null) {
					JLabel spouseName = new JLabel(spouse.getName());
					spouseName.setBounds(160 + s*100, 190, 150, 20);
					mainCard.add(spouseName);
					
					JButton removeSpouse = new JButton("Remove");
					removeSpouse.setActionCommand(Integer.toString(spouse.getID()));
					removeSpouse.setBounds(160 + s*100, 220, 60, 20);
					removeSpouse.addActionListener(new ActionListener() {

						@Override
						public void actionPerformed(ActionEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							int id = Integer.parseInt(e.getActionCommand());
							Character ch = person.removeSpouse(id);
							ch.removeSpouse(person.getID());
							start(person.getID(), true, gender);
							cl.show(mainCards, "Main Card");
						}
					});
					
					mainCard.add(spouseName);
					mainCard.add(removeSpouse);
				}
			}
			
			mainCard.add(spouseLabel);
			mainCard.add(addSpouse);
			
			JLabel issue = new JLabel("Children:");
			issue.setBounds(80, 250, 150, 20);
			
			JButton addIssue = new JButton("Add");
			addIssue.setBounds(10, 250, 60, 20);
			addIssue.addActionListener(new ActionListener() {

				@Override
				public void actionPerformed(ActionEvent e) {
					CardLayout cl = (CardLayout) (mainCards.getLayout());
					chooseCharacter(person, Relation.CHILD, null);
					cl.show(mainCards, "Choose Character Card");
				}
				
			});
			
			ArrayList<Character> children = person.getChildren();
			for(int c = 0; c < children.size(); ++c) {
				Character child = children.get(c);
				if(child != null) {
					JLabel childLabel = new JLabel(child.getName());
					childLabel.setBounds(80, 280 + c*30, 150, 20);
					mainCard.add(childLabel);
					
					JButton addChild = new JButton("Remove");
					addChild.setActionCommand(Integer.toString(child.getID()));
					addChild.setBounds(10, 280 + c*30, 60, 20);
					addChild.addActionListener(new ActionListener() {
	
						@Override
						public void actionPerformed(ActionEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							int id = Integer.parseInt(e.getActionCommand());
							Character ch = person.removeChild(id);
							if(ch.getFather() == person)
								ch.setFather(null);
							else if(ch.getMother() == person)
								ch.setMother(null);
							start(person.getID(), true, gender);
							cl.show(mainCards, "Main Card");
						}
						
					});
					mainCard.add(addChild);
				}
			}
			
			editButton.setText("Done");
			editButton.addActionListener(new ActionListener() {

				@Override
				public void actionPerformed(ActionEvent e) {
					CardLayout cl = (CardLayout) (mainCards.getLayout());
					
					if(edit) {
						person.setGender(gender);
						person.setBirthday(bdayLabel.getText());
						person.setDeathday(ddayLabel.getText());
					}

					printData(CHARACTER);
					
					start(id, !edit, gender);
					cl.show(mainCards, "Main Card");
				}
			});

			mainCard.add(genderLabel);
			mainCard.add(switchGender);
			mainCard.add(issue);
			mainCard.add(addIssue);
			mainCard.add(nmLabel);
			mainCard.add(bday);
			mainCard.add(bdayLabel);
			mainCard.add(dday);
			mainCard.add(ddayLabel);
			mainCard.add(addDad);
			mainCard.add(dadLabel);
			mainCard.add(momLabel);
			mainCard.add(momName);
		}
		else {		
			JLabel nmLabel = new JLabel(person.getName());
			nmLabel.setFont(new Font("Helvetica", Font.BOLD, 24));
			int width = (int) Math.ceil(nmLabel.getPreferredSize().getWidth());
			nmLabel.setBounds((WIDTH-width)/2, 10, width, 50);
			
			JLabel genderLabel = new JLabel("Gender: " + person.getGender());
			genderLabel.setBounds(10, 40, 100, 20);
			
			JLabel bdayLabel = new JLabel("Birthday: " + person.getBirthday());
			bdayLabel.setBounds(10, 70, 200, 20);
			
			JLabel ddayLabel = new JLabel("Deathday: " + person.getDeathday());
			ddayLabel.setBounds(10, 100, 200, 20);
			
			JLabel dadLabel = new JLabel("Father:");
			dadLabel.setBounds(10, 130, 50, 20);
			
			if(person.getFather() != null) {
				JLabel dadName = new JLabel("<html><u>" + person.getFatherName() + "</u></html>");
				dadName.setBounds(80, 130, (int) Math.ceil(dadName.getPreferredSize().getWidth()), 20);
				dadName.addMouseListener(new MouseListener() {
		
					@Override
					public void mouseClicked(MouseEvent e) {
						CardLayout cl = (CardLayout) (mainCards.getLayout());
						start(person.getFather().getID(), false, gender);
						cl.show(mainCards, "Main Card");
					}
		
					@Override
					public void mousePressed(MouseEvent e) {
						
					}
		
					@Override
					public void mouseReleased(MouseEvent e) {
						
					}
		
					@Override
					public void mouseEntered(MouseEvent e) {
						CardLayout cl = (CardLayout) (mainCards.getLayout());
						dadName.setForeground(Color.BLUE);
						dadName.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
						cl.show(mainCards, "Main Card");
					}
		
					@Override
					public void mouseExited(MouseEvent e) {
						CardLayout cl = (CardLayout) (mainCards.getLayout());
						dadName.setForeground(Color.BLACK);
						dadName.setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
						cl.show(mainCards, "Main Card");
					}
					
				});

				mainCard.add(dadName);
			}
			
			JLabel momLabel = new JLabel("Mother:");
			momLabel.setBounds(10, 160, 50, 20);
			
			if(person.getMother() != null) {
				JLabel momName = new JLabel("<html><u>" + person.getMotherName() + "</u></html>");
				momName.setBounds(80, 160, (int) Math.ceil(momName.getPreferredSize().getWidth()), 20);
				momName.addMouseListener(new MouseListener() {
		
					@Override
					public void mouseClicked(MouseEvent e) {
						CardLayout cl = (CardLayout) (mainCards.getLayout());
						start(person.getMother().getID(), false, gender);
						cl.show(mainCards, "Main Card");
					}
		
					@Override
					public void mousePressed(MouseEvent e) {
						
					}
		
					@Override
					public void mouseReleased(MouseEvent e) {
						
					}
		
					@Override
					public void mouseEntered(MouseEvent e) {
						CardLayout cl = (CardLayout) (mainCards.getLayout());
						momName.setForeground(Color.BLUE);
						momName.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
						cl.show(mainCards, "Main Card");
					}
		
					@Override
					public void mouseExited(MouseEvent e) {
						CardLayout cl = (CardLayout) (mainCards.getLayout());
						momName.setForeground(Color.BLACK);
						momName.setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
						cl.show(mainCards, "Main Card");
					}
					
				});
				
				mainCard.add(momName);
			}
			
			JLabel spouseLabel = new JLabel("Spouses:");
			spouseLabel.setBounds(10, 190, 60, 20);
			
			ArrayList<Character> spouses = person.getSpouses();
			ArrayList<Character> children = person.getChildren();
			@SuppressWarnings("unchecked")
			ArrayList<Character> others = (ArrayList<Character>) children.clone();
			int count = 0;
			
			for(int s = 0; s < spouses.size(); ++s) {
				Character spouse = spouses.get(s);
				
				if(spouse != null) {
					count++;
					
					JLabel spouseName = new JLabel("<html><u>" + spouse.getName() + "</u></html>");
					spouseName.setBounds(80 + s*120, 190, (int) Math.ceil(spouseName.getPreferredSize().getWidth()), 20);
					spouseName.addMouseListener(new MouseListener() {
						
						@Override
						public void mouseClicked(MouseEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							start(spouse.getID(), false, gender);
							cl.show(mainCards, "Main Card");
						}
		
						@Override
						public void mousePressed(MouseEvent e) {
							
						}
		
						@Override
						public void mouseReleased(MouseEvent e) {
							
						}
		
						@Override
						public void mouseEntered(MouseEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							spouseName.setForeground(Color.BLUE);
							spouseName.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
							cl.show(mainCards, "Main Card");
						}
		
						@Override
						public void mouseExited(MouseEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							spouseName.setForeground(Color.BLACK);
							spouseName.setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
							cl.show(mainCards, "Main Card");
						}
						
					});
					
					int mult = 0;

					for(int c = 0; c < children.size(); ++c) {
						Character child = children.get(c);
						if(child != null && (child.getFather() == spouse || child.getMother() == spouse)) {
							others.remove(child);
							
							JLabel childLabel = new JLabel("<html><u>" + child.getName() + "</u></html>");
							childLabel.setBounds(80 + s*120, 220 + mult*30, (int) Math.ceil(childLabel.getPreferredSize().getWidth()), 20);
							childLabel.addMouseListener(new MouseListener() {
				
								@Override
								public void mouseClicked(MouseEvent e) {
									CardLayout cl = (CardLayout) (mainCards.getLayout());
									start(child.getID(), false, gender);
									cl.show(mainCards, "Main Card");
								}
				
								@Override
								public void mousePressed(MouseEvent e) {
									
								}
				
								@Override
								public void mouseReleased(MouseEvent e) {
									
								}
				
								@Override
								public void mouseEntered(MouseEvent e) {
									CardLayout cl = (CardLayout) (mainCards.getLayout());
									childLabel.setForeground(Color.BLUE);
									childLabel.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
									cl.show(mainCards, "Main Card");
								}
				
								@Override
								public void mouseExited(MouseEvent e) {
									CardLayout cl = (CardLayout) (mainCards.getLayout());
									childLabel.setForeground(Color.BLACK);
									childLabel.setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
									cl.show(mainCards, "Main Card");
								}
							});
							
							mainCard.add(childLabel);
						
							mult++;
						}
					}
					
					mainCard.add(spouseName);
				}
			}
			for(int c = 0; c < others.size(); ++c) {
				Character child = others.get(c);
				
				if(child != null) {
					JLabel childLabel = new JLabel("<html><u>" + child.getName() + "</u></html>");
					childLabel.setBounds(80 + count*120, 220 + c*30, (int) Math.ceil(childLabel.getPreferredSize().getWidth()), 20);
					childLabel.addMouseListener(new MouseListener() {
		
						@Override
						public void mouseClicked(MouseEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							start(child.getID(), false, gender);
							cl.show(mainCards, "Main Card");
						}
		
						@Override
						public void mousePressed(MouseEvent e) {
							
						}
		
						@Override
						public void mouseReleased(MouseEvent e) {
							
						}
		
						@Override
						public void mouseEntered(MouseEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							childLabel.setForeground(Color.BLUE);
							childLabel.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
							cl.show(mainCards, "Main Card");
						}
		
						@Override
						public void mouseExited(MouseEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							childLabel.setForeground(Color.BLACK);
							childLabel.setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
							cl.show(mainCards, "Main Card");
						}
						
					});
					
					mainCard.add(childLabel);
				}
			}
				
			JLabel issue = new JLabel("Children:");
			issue.setBounds(10, 220, 100, 20);
			
			editButton.addActionListener(new ActionListener() {

				@Override
				public void actionPerformed(ActionEvent e) {
					CardLayout cl = (CardLayout) (mainCards.getLayout());
					start(id, !edit, person.getGenderInt());
					cl.show(mainCards, "Main Card");
				}
			});

			mainCard.add(genderLabel);
			mainCard.add(spouseLabel);
			mainCard.add(issue);
			mainCard.add(nmLabel);
			mainCard.add(bdayLabel);
			mainCard.add(ddayLabel);
			mainCard.add(dadLabel);
			mainCard.add(momLabel);
		}
		
		mainCard.add(editButton);
		
		mainCards.add(mainCard, MCARD);
	}
	public static void addCharacter(Relation r) {
		JPanel addCharCard = new JPanel(null);
		
		String name = "";
		int gender = 0;

		if(r == null || (r.getType() != Relation.FATHER && r.getType() != Relation.MOTHER)) {
			JTextField nameInput = new JTextField();
			nameInput.setPreferredSize(new Dimension(100, 20));
			JLabel nameLabel = new JLabel("New Character Name?");
			
			JPanel namePanel = new JPanel(new BorderLayout());
			namePanel.add(nameLabel, BorderLayout.WEST);
			namePanel.add(nameInput, BorderLayout.EAST);
			
			Object[] options = { "Male", "Female" };
			
			int selection = JOptionPane.showOptionDialog(null, namePanel, "New Character", JOptionPane.DEFAULT_OPTION, JOptionPane.PLAIN_MESSAGE, null, options, options[0]);
			
			name = nameInput.getText();
			if(selection == 0)
				gender = 1;
			else
				gender = -1;
		}
		else if(r.getType() == Relation.FATHER) {
			name = JOptionPane.showInputDialog(null, "New Character Name?", "New Character", JOptionPane.INFORMATION_MESSAGE);
			gender = 1;
		}
		else if(r.getType() == Relation.MOTHER) {
			name = JOptionPane.showInputDialog(null, "New Character Name?", "New Character", JOptionPane.INFORMATION_MESSAGE);
			gender = -1;
		}
		
		Character person = new Character(name, -1);
		person.setGender(gender);
		
		charList.add(person);
		
		if(r == null) {
			JLabel dadLabel = new JLabel("Father:");
			dadLabel.setBounds(10, 130, 60, 20);
			
			JLabel momLabel = new JLabel("Mother:");
			momLabel.setBounds(10, 160, 60, 20);
			
			JLabel spouseLabel = new JLabel("Spouses:");
			spouseLabel.setBounds(10, 190, 80, 20);
			
			JLabel issue = new JLabel("Children:");
			issue.setBounds(10, 220, 150, 20);

			addCharCard.add(issue);
			addCharCard.add(dadLabel);
			addCharCard.add(momLabel);
			addCharCard.add(spouseLabel);
		}
		else {
			Relation r_inv = r.getInverse();
			if(r_inv.getType() == Relation.CHILD) {
				JLabel dadLabel = new JLabel("Father:");
				dadLabel.setBounds(10, 130, 60, 20);
				
				JLabel momLabel = new JLabel("Mother:");
				momLabel.setBounds(10, 160, 60, 20);
				
				JLabel spouseLabel = new JLabel("Spouses:");
				spouseLabel.setBounds(10, 190, 80, 20);

				person.addSpouse(null);
				
				Character child = charList.get(r_inv.getRelation());
				person.addChild(child);
				child.setRelation(r);
				
				JLabel issue = new JLabel("Children:");
				issue.setBounds(10, 220, 150, 20);
				
				JLabel childLabel = new JLabel(child.getName());
				childLabel.setBounds(80, 220, 150, 20);
				
				addCharCard.add(issue);
				addCharCard.add(childLabel);
				addCharCard.add(dadLabel);
				addCharCard.add(momLabel);
				addCharCard.add(spouseLabel);
			}
			else if(r_inv.getType() == Relation.SPOUSE) {
				JLabel dadLabel = new JLabel("Father:");
				dadLabel.setBounds(10, 130, 60, 20);
				
				JLabel momLabel = new JLabel("Mother:");
				momLabel.setBounds(10, 160, 60, 20);
				
				JLabel spouseLabel = new JLabel("Spouses:");
				spouseLabel.setBounds(10, 190, 80, 20);
				
				Character spouse = charList.get(r_inv.getRelation());
				person.addSpouse(spouse);
				spouse.addSpouse(person);
				
				JLabel spouseName = new JLabel(spouse.getName());
				spouseName.setBounds(100, 190, 80, 20);
				
				person.addChild(null);
				
				JLabel issue = new JLabel("Children:");
				issue.setBounds(10, 220, 150, 20);
				
				addCharCard.add(issue);
				addCharCard.add(spouseName);
				addCharCard.add(dadLabel);
				addCharCard.add(momLabel);
				addCharCard.add(spouseLabel);
			}
			else if(r_inv.getType() == Relation.FATHER) {
				JLabel dadLabel = new JLabel("Father:");
				dadLabel.setBounds(10, 130, 60, 20);
				
				Character dad = charList.get(r_inv.getRelation());
				person.setFather(dad);
				dad.addChild(person);
				
				JLabel dadName = new JLabel(dad.getName());
				dadName.setBounds(80, 130, 60, 20);
				
				JLabel momLabel = new JLabel("Mother:");
				momLabel.setBounds(10, 160, 60, 20);
				
				JLabel spouseLabel = new JLabel("Spouses:");
				spouseLabel.setBounds(10, 190, 80, 20);
				
				person.addSpouse(null);
				person.addChild(null);
				
				JLabel issue = new JLabel("Children:");
				issue.setBounds(10, 220, 150, 20);
				
				addCharCard.add(issue);
				addCharCard.add(dadName);
				addCharCard.add(dadLabel);
				addCharCard.add(momLabel);
				addCharCard.add(spouseLabel);
			}
			else if(r_inv.getType() == Relation.MOTHER) {
				JLabel dadLabel = new JLabel("Father:");
				dadLabel.setBounds(10, 130, 60, 20);
				
				JLabel momLabel = new JLabel("Mother:");
				momLabel.setBounds(10, 160, 60, 20);
				
				Character mom = charList.get(r_inv.getRelation());
				
				JLabel momName = new JLabel(mom.getName());
				momName.setBounds(80, 130, 60, 20);
				
				person.setMother(mom);
				mom.addChild(person);
				
				JLabel spouseLabel = new JLabel("Spouses:");
				spouseLabel.setBounds(10, 190, 80, 20);

				person.addSpouse(null);
				person.addChild(null);
				
				JLabel issue = new JLabel("Children:");
				issue.setBounds(10, 220, 150, 20);
				
				addCharCard.add(issue);
				addCharCard.add(momName);
				addCharCard.add(dadLabel);
				addCharCard.add(momLabel);
				addCharCard.add(spouseLabel);
			}
		}
		
		JTextField nmLabel = new JTextField(person.getName());
		nmLabel.setBounds(175, 10, 150, 20);
		
		JLabel bday = new JLabel("Birthday:");
		bday.setBounds(10, 70, 70, 20);
		
		JTextField bdayLabel = new JTextField();
		bdayLabel.setBounds(80, 70, 150, 20);
		
		JLabel dday = new JLabel("Deathday:");
		dday.setBounds(10, 100, 70, 20);
		
		JTextField ddayLabel = new JTextField();
		ddayLabel.setBounds(80, 100, 150, 20);

		JLabel genderLabel = new JLabel();
		genderLabel.setBounds(10, 40, 100, 20);
		if(gender == Character.FEMALE)
			genderLabel.setText("Gender: Female");
		else
			genderLabel.setText("Gender: Male");
		
		
		JButton save = new JButton("Save");
		save.setBounds(440, 10, 50, 20);
		save.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				CardLayout cl = (CardLayout) (mainCards.getLayout());
				
				person.setBirthday(bdayLabel.getText());
				person.setDeathday(ddayLabel.getText());
				
				printData(CHARACTER);
				
				start(person.getID(), false, person.getGenderInt());
				cl.show(mainCards, "Main Card");
			}
		});

		addCharCard.add(genderLabel);
		addCharCard.add(save);
		addCharCard.add(nmLabel);
		addCharCard.add(bday);
		addCharCard.add(bdayLabel);
		addCharCard.add(dday);
		addCharCard.add(ddayLabel);
		
		mainCards.add(addCharCard, NCHAR);
	}
	public static void chooseCharacter(Character self, int type, String search) {
		JPanel chooseCharCard = new JPanel(null);
		
		//System.out.println("relation: " + type);
		
		JButton back = new JButton("Back");
		back.setBounds(10, 10, 60, 20);
		back.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				CardLayout cl = (CardLayout) (mainCards.getLayout());
				start(self.getID(), true, self.getGenderInt());
				cl.show(mainCards, "Main Card");
			}
		});
		chooseCharCard.add(back);
		
		JButton newChar = new JButton("New");
		newChar.setBounds(10, 40, 60, 20);
		newChar.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				CardLayout cl = (CardLayout) (mainCards.getLayout());
				addCharacter(new Relation(self.getID(), charList.size(), type));
				cl.show(mainCards, "New Character Card");
			}
		});
		chooseCharCard.add(newChar);
		
		JLabel searchLabel = new JLabel("Search:");
		searchLabel.setBounds(145, 20, 55, 20);
		chooseCharCard.add(searchLabel);

		JTextField searchField = new JTextField();
		searchField.setBounds(200, 20, 200, 20);
		
		JPanel panel = new JPanel(null);
				
		getPossibleChars(panel, self, type, searchField.getText());
		
		searchField.getDocument().addDocumentListener(new DocumentListener() {

			@Override
			public void insertUpdate(DocumentEvent e) {
				//System.out.println("Insert Update: " + searchField.getText());
				
				getPossibleChars(panel, self, type, searchField.getText());
				chooseCharCard.revalidate();
				chooseCharCard.repaint();
			}

			@Override
			public void removeUpdate(DocumentEvent e) {
				//System.out.println("Remove Update");	
				
				getPossibleChars(panel, self, type, searchField.getText());
				chooseCharCard.revalidate();
				chooseCharCard.repaint();
			}

			@Override
			public void changedUpdate(DocumentEvent e) {
				
			}
		});
	
		chooseCharCard.add(searchField);
		
		JPanel scrollPanel = new JPanel(new BorderLayout());
		scrollPanel.setBounds(100, 50, 350, 400);
		chooseCharCard.add(scrollPanel);

		JScrollPane scrollPane = new JScrollPane(panel);
		scrollPane.setPreferredSize(new Dimension(250, 400));
		
		scrollPanel.add(scrollPane, BorderLayout.CENTER);
		
		chooseCharCard.add(scrollPanel);
		
		mainCards.add(chooseCharCard, CCHAR);
	}
	public static JPanel getPossibleChars(JPanel panel, Character self, int type, String search) {
		panel.removeAll();

		//System.out.println("relation: " + type);
		
		int level = 0;
		
		for(int i = 0; i < charList.size(); ++i) {
			Character c = charList.get(i);
			
			boolean display = false;
			
			if(type == Relation.FATHER && c.getGenderInt() == Character.MALE) {
				display = true;
			}
			else if(type == Relation.MOTHER && c.getGenderInt() == Character.FEMALE) {
				display = true;
			}
			else if(type == Relation.CHILD && !self.isChild(i))
				display = true;
			else if(type == Relation.SPOUSE && !self.isSpouse(i))
				display = true;
			
			if(display) {
				if(search == null || c.getName().contains(search)) {
					//System.out.println("Char: " + c.getName() + ", Search: " + search);
					JLabel nameLabel = new JLabel(c.getName());
					nameLabel.setBounds(10, 10+level*55, 100, 20);
					
					JLabel born = new JLabel("Born: " + c.getBirthday());
					//lifeLabel.setText("( " + c.getBirthday() + " - " + c.getDeathday() + " )");
					born.setBounds(30, 25+level*55, 170, 20);
					
					JLabel died = new JLabel("Died: " + c.getDeathday());
					//lifeLabel.setText("( " + c.getBirthday() + " - " + c.getDeathday() + " )");
					died.setBounds(30, 40+level*55, 170, 20);
					
					JButton choose = new JButton("Choose");
					choose.setBounds(250, 25 + level*55, 60, 20);
					choose.setActionCommand(Integer.toString(c.getID()));
					choose.addActionListener(new ActionListener() {
		
						@Override
						public void actionPerformed(ActionEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							
							Character choice = charList.get(Integer.parseInt(e.getActionCommand()));
							
							Relation r = new Relation(self.getID(), choice.getID(), type);
							
							//System.out.println(r);
							self.setRelation(r);
							choice.setRelation(r.getInverse());
							
							start(self.getID(), true, self.getGenderInt());
							cl.show(mainCards, "Main Card");
						}
					});
					
					level++;

					panel.add(died);
					panel.add(born);
					panel.add(nameLabel);
					panel.add(choose);
				}
			}
		}
		panel.setPreferredSize(new Dimension(400, 20 + level*55));
		
		return panel;
	}
	public static void printData(int type) {
		if(type == CHARACTER) {
			/**
			 * Character ID (int)
			 * Name (String)
			 * Gender (int, Female: -1, Male: 1)
			 * Birthday (String)
			 * Deathday (String)
			 * Father (int, Character ID)
			 * Mother (int, Character ID)
			 * Spouses (ints, Character ID, separated by ",")
			 * Children (ints, Character ID, separated by ",")
			 */
			try {
				BufferedWriter writer = new BufferedWriter(new FileWriter(new File("src/characters.txt")));
				String line = "";
				
				for(int i = 0; i < charList.size(); ++i) {
					Character person = charList.get(i);
					
					line = line + person.getID() + ";" + person.getName() + ";" + person.getGenderInt() + ";"
							+ person.getBirthday() + ";" + person.getDeathday() + ";";
					if(person.getFather() == null)
						line = line + "-1;";
					else
						line = line + person.getFather().getID() + ";";
					
					if(person.getMother() == null)
						line = line + "-1;";
					else
						line = line + person.getMother().getID() + ";";
					
					if(person.getSpouses().get(0) == null)
						line = line + "-1";
					else
						for(int s = 0; s < person.getSpouses().size(); s++) {
							Character spouse = person.getSpouses().get(s);
							
							if(s == 0)
								line = line + spouse.getID();
							else
								line = line + "," + spouse.getID();

						}
					
					line = line + ";";
					
					if(person.getChildren().get(0) == null)
						line = line + "-1";
					else
						for(int c = 0; c < person.getChildren().size(); ++c) {
							Character child = person.getChildren().get(c);
							
							if(c == 0)
								line = line + child.getID();
							else
								line = line + "," + child.getID();
						}
						
					line = line + ";\n";
				}
				
				writer.write(line);
				
				writer.close();
			}
			catch(IOException e) {
				System.out.println(e.getMessage());
			}
		}
		else if(type == FIEF) {
			/**
			 * Fief ID (int)
			 * Name (String)
			 * Fief Type (int)
			 * Ruler ID (int)
			 * Ruler Start Date (String)
			 * Ruler End Date (String)
			 */
		}
		else
			System.out.println("Error: Invalid Type");
	}
	public static void readData(int type) {
		if(type == CHARACTER) {
			charList.clear();
			try {
				BufferedReader reader = new BufferedReader(new FileReader(new File("src/characters.txt")));
				String line;
				while(!((line = reader.readLine()) == null)) {
					String[] values = line.split(";");
					Character person = new Character(values[1], -1);
					person.setGender(Integer.parseInt(values[2]));
					
					person.setBirthday(values[3]);
					person.setDeathday(values[4]);
					
					if(person.getID() != Integer.parseInt(values[0]))
						System.out.println("Error: Mismatched IDs. ID Read: " + values[0] + ", ID Set: " + person.getID());
					else {
						person.addRelation(new Relation(person.getID(), Integer.parseInt(values[5]), Relation.FATHER));
						person.addRelation(new Relation(person.getID(), Integer.parseInt(values[6]), Relation.MOTHER));
						String[] spouse = values[7].split(",");
						for(int i = 0; i < spouse.length; ++i)
							person.addRelation(new Relation(person.getID(), Integer.parseInt(spouse[i]), Relation.SPOUSE));
						String[] issue = values[8].split(",");
						for(int i = 0; i < issue.length; ++i)
							person.addRelation(new Relation(person.getID(), Integer.parseInt(issue[i]), Relation.CHILD));
					}
					charList.add(person);
				}
				setCharacters();
				reader.close();
			} catch (IOException e) {
				System.out.println(e.getMessage());
			}
		}
		else if(type == FIEF) {
			fiefList.clear();
			try {
				BufferedReader reader = new BufferedReader(new FileReader(new File("src/fiefs.txt")));
				String line;
				while(!((line = reader.readLine()) == null)) {
					String[] values = line.split(";");
					int fiefID = Integer.parseInt(values[0]);
					
					Fief fief;
					if(fiefID < fiefList.size())
						fief = fiefList.get(fiefID);
					else
						fief = new Fief(fiefID, values[1], Integer.parseInt(values[2]));

					Character ruler = charList.get(Integer.parseInt(values[3]));
					
					System.out.println(getDate(values[4]));
					System.out.println(getDate(values[5]));
					
				}
			} catch (IOException e) {
				System.out.println(e.getMessage());
			}
		}
		else
			System.out.println("Error: Invalid Type");
	}
	public static LocalDate getDate(String date) {
		String[] parts = date.split(" ");
		if(parts.length == 3)
			return LocalDate.of(Integer.parseInt(parts[2]), getMonth(parts[1]), Integer.parseInt(parts[0]));
		else if(parts.length == 1)
			return LocalDate.of(Integer.parseInt(parts[0]), 6, 15);
		else if(parts[0].contains(".")) {
			return LocalDate.of(Integer.parseInt(parts[1]), 6, 15);
		}
		else
			return LocalDate.of(Integer.parseInt(parts[1]), getMonth(parts[0]), 15);
	}
	public static int getMonth(String m) {
		if(m.equals("January"))
			return 1;
		else if(m.equals("February"))
			return 2;
		else if(m.equals("March"))
			return 3;
		else if(m.equals("April"))
			return 4;
		else if(m.equals("May"))
			return 5;
		else if(m.equals("June"))
			return 6;
		else if(m.equals("July"))
			return 7;
		else if(m.equals("August"))
			return 8;
		else if(m.equals("September"))
			return 9;
		else if(m.equals("October"))
			return 10;
		else if(m.equals("November"))
			return 11;
		else if(m.equals("December"))
			return 12;
		else {
			System.out.println("Invalid Month Error: " + m);
			return -1;
		}
	}
	public static void setCharacters() {
		for(int i = 0; i < charList.size(); ++i) {
			Character person = charList.get(i);
			ArrayList<Relation> relations = person.getRelations();
			for(int j = 0; j < relations.size(); ++j) {
				Relation r = relations.get(j);
				Character target = new Character();
				if(r.getRelation() == -1)
					target = null;
				else
					target = charList.get(r.getRelation());
				
				if(r.getType() == Relation.MOTHER)
					person.setMother(target);
				else if(r.getType() == Relation.FATHER)
					person.setFather(target);
				else if(r.getType() == Relation.CHILD)
					person.addChild(target);
				else if(r.getType() == Relation.SPOUSE)
					person.addSpouse(target);
				else
					System.out.println("Error: Invalid Relation Type");
			}
		}
	}
}
