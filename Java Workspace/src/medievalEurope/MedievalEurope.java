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
	final static int TITLE = 2;
	
	final static int WIDTH = 800;
	final static int HEIGHT = 800;
	
	protected static ArrayList<Character> charList = new ArrayList<Character>();
	private static ArrayList<Fief> fiefList = new ArrayList<Fief>();
	private static ArrayList<Title> titleList = new ArrayList<Title>();
	
	static JPanel mainCards = new JPanel(new CardLayout());
	final static String NCHAR = "New Character Card";
	final static String MCARD = "Main Card";
	final static String CCHAR = "Choose Character Card";
	final static String CTCARD = "Choose Title Card";
	final static String FPCARD = "Fief Page Card";

	public static void main(String[] args) {
		MedievalEurope frame = new MedievalEurope();
		frame.setVisible(true);
	}
	public MedievalEurope() {
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setSize(WIDTH, HEIGHT);
		setResizable(false);
		
		Container pane = getContentPane();
		
		int startChar = 16;

		readData(CHARACTER);
		readData(FIEF);
		readData(TITLE);
		start(startChar, false);
		
		pane.add(mainCards, BorderLayout.CENTER);
	}
	public static void start(int id, boolean edit) {
		JPanel mainCard = new JPanel(null);
		
		Character person = charList.get(id);
	
		JButton editButton = new JButton("Edit");
		editButton.setBounds(WIDTH-60, 10, 50, 20);

		int labelWidth = 150;
		
		if(edit) {
			JLabel nameLabel = new JLabel("Name:");
			nameLabel.setBounds(WIDTH/2 - 115, 10, 40, 20);
			
			JTextField nmLabel = new JTextField(person.getName());
			nmLabel.setBounds(WIDTH/2 - 75, 10, 150, 20);

			JLabel nnameLabel = new JLabel("Nickname:");
			nnameLabel.setBounds(WIDTH/2 - 145, 45, 70, 20);
			
			JTextField nicknameLabel = new JTextField(person.getNickName());
			nicknameLabel.setBounds((WIDTH-150)/2, 45, 150, 20);
			
			JLabel heldTitles = new JLabel("Titles Held:");
			int w = (int) Math.ceil(heldTitles.getPreferredSize().getWidth());
			heldTitles.setBounds(WIDTH - labelWidth - 120, 75, w, 20);
			mainCard.add(heldTitles);
			
			JPanel panel = new JPanel(null);
			int level = 0;
			
			for(int i = 0; i < person.getTitles().size(); ++i) {
				Title title = person.getTitles().get(i);
				
				JLabel label = new JLabel(title.getTitle());
				w = (int) Math.ceil(label.getPreferredSize().getWidth());
				label.setBounds(50 + (labelWidth - w)/2, 8 + 45*level, w, 20);
				
				JLabel reign = new JLabel("(" + title.getStartDate().getYear() + " - " + title.getEndDate().getYear() + ")");
				w = (int) Math.ceil(reign.getPreferredSize().getWidth());
				reign.setBounds(50 + (labelWidth - w)/2, 23 + 45*level, w, 20);
				
				if(title.getPredecessor() == null) {
					JButton add = new JButton("+");
					//back.setFont(new Font("Helvetica", 16, Font.BOLD));
					add.setBounds(10, 10 + 45*level, 30, 30);
					add.addActionListener(new ActionListener() {

						@Override
						public void actionPerformed(ActionEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							chooseCharacter(new Relation(person, title, Relation.PREDECESSOR), null);
							cl.show(mainCards, "Choose Title Card");
						}
					});
					panel.add(add);				
				}
				
				if(title.getSuccessor() == null) {
					JButton add = new JButton("+");
					//next.setFont(new Font("Helvetica", 16, Font.BOLD));
					add.setBounds(labelWidth + 60, 10 + 45*level, 30, 30);
					add.addActionListener(new ActionListener() {

						@Override
						public void actionPerformed(ActionEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							chooseCharacter(new Relation(person, title, Relation.SUCCESSOR), null);
							cl.show(mainCards, "Choose Title Card");
						}
					});
					panel.add(add);
				}
				
				panel.add(label);
				panel.add(reign);
				
				level++;
			}
			
			JButton addTitle = new JButton("Add New Title");
			addTitle.setBounds(50, 10 + 45*level, labelWidth, 30);
			panel.add(addTitle);
			
			panel.setPreferredSize(new Dimension(labelWidth + 100, 20 + level*55));
			
			JPanel scrollPanel = new JPanel(new BorderLayout());
			scrollPanel.setBounds(WIDTH - labelWidth - 120, 95, labelWidth + 104, 400);

			JScrollPane scrollPane = new JScrollPane(panel);
			
			scrollPanel.add(scrollPane, BorderLayout.CENTER);
			
			mainCard.add(scrollPanel);
			
			editButton.addActionListener(new ActionListener() {

				@Override
				public void actionPerformed(ActionEvent e) {
					CardLayout cl = (CardLayout) (mainCards.getLayout());
					start(id, !edit);
					cl.show(mainCards, "Main Card");
				}
			});
			
			JLabel bday = new JLabel("Birthday:");
			bday.setBounds(10, 105, 70, 20);
			
			JTextField bdayLabel = new JTextField(person.getBirthday());
			bdayLabel.setBounds(80, 105, 150, 20);
			
			JLabel dday = new JLabel("Deathday:");
			dday.setBounds(10, 135, 70, 20);
			
			JTextField ddayLabel = new JTextField(person.getDeathday());
			ddayLabel.setBounds(80, 135, 150, 20);

			JLabel genderLabel = new JLabel();
			genderLabel.setBounds(80, 75, 100, 20);
			
			
			if(person.getGenderInt() == Character.FEMALE)
				genderLabel.setText("Gender: Female");
			else
				genderLabel.setText("Gender: Male");
			
			JButton switchGender = new JButton("Switch");
			switchGender.setBounds(10, 75, 60, 20);
			switchGender.addActionListener(new ActionListener() {

				@Override
				public void actionPerformed(ActionEvent e) {
					CardLayout cl = (CardLayout) (mainCards.getLayout());

					person.setBirthday(bdayLabel.getText());
					person.setDeathday(ddayLabel.getText());
					
					person.setGender(person.getGenderInt() * -1);
					
					start(person.getID(), true);
					cl.show(mainCards, "Main Card");
				}
			});
			
			JLabel dadLabel = new JLabel("Father:");
			dadLabel.setBounds(80, 165, 60, 20);
			
			JLabel dadName = new JLabel(person.getFatherName());
			dadName.setBounds(140, 165, 150, 20);
			
			JButton addDad = new JButton("Add");
			addDad.setActionCommand(Integer.toString(Relation.FATHER));
			addDad.setBounds(10, 165, 60, 20);
			addDad.addActionListener(new ActionListener() {

				@Override
				public void actionPerformed(ActionEvent e) {	
					CardLayout cl = (CardLayout) (mainCards.getLayout());
					chooseCharacter(new Relation(person, null, Relation.FATHER), null);
					cl.show(mainCards, "Choose Character Card");
				}
			});
			if(person.getFather() != null)
				addDad.setText("Change");

			mainCard.add(dadName);
			
			JLabel momLabel = new JLabel("Mother:");
			momLabel.setBounds(80, 195, 60, 20);
			
			JLabel momName = new JLabel(person.getMotherName());
			momName.setBounds(140, 195, 100, 20);
			
			JButton addMom = new JButton("Add");
			addMom.setBounds(10, 195, 60, 20);
			addMom.addActionListener(new ActionListener() {

				@Override
				public void actionPerformed(ActionEvent e) {
					CardLayout cl = (CardLayout) (mainCards.getLayout());
					chooseCharacter(new Relation(person, null, Relation.MOTHER), null);
					cl.show(mainCards, "Choose Character Card");
				}
				
			});
			if(person.getMother() != null)
				addMom.setText("Change");
			
			mainCard.add(addMom);
			
			JLabel spouseLabel = new JLabel("Spouses:");
			spouseLabel.setBounds(80, 225, 80, 20);
			
			JButton addSpouse = new JButton("Add");
			addSpouse.setBounds(10, 225, 60, 20);
			addSpouse.addActionListener(new ActionListener() {

				@Override
				public void actionPerformed(ActionEvent e) {
					CardLayout cl = (CardLayout) (mainCards.getLayout());
					chooseCharacter(new Relation(person, null, Relation.SPOUSE), null);
					cl.show(mainCards, "Choose Character Card");
				}
			});
			
			ArrayList<Character> spouses = person.getSpouses();
			for(int s = 0; s < spouses.size(); ++s) {
				Character spouse = spouses.get(s);
				if(spouse != null) {
					JLabel spouseName = new JLabel(spouse.getName());
					spouseName.setBounds(160 + s*100, 225, 150, 20);
					mainCard.add(spouseName);
					
					JButton removeSpouse = new JButton("Remove");
					removeSpouse.setActionCommand(Integer.toString(spouse.getID()));
					removeSpouse.setBounds(160 + s*100, 255, 60, 20);
					removeSpouse.addActionListener(new ActionListener() {

						@Override
						public void actionPerformed(ActionEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							int id = Integer.parseInt(e.getActionCommand());
							Character ch = person.removeSpouse(id);
							ch.removeSpouse(person.getID());
							start(person.getID(), true);
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
			issue.setBounds(80, 285, 150, 20);
			
			JButton addIssue = new JButton("Add");
			addIssue.setBounds(10, 285, 60, 20);
			addIssue.addActionListener(new ActionListener() {

				@Override
				public void actionPerformed(ActionEvent e) {
					CardLayout cl = (CardLayout) (mainCards.getLayout());
					chooseCharacter(new Relation(person, null, Relation.CHILD), null);
					cl.show(mainCards, "Choose Character Card");
				}
				
			});
			
			ArrayList<Character> children = person.getChildren();
			for(int c = 0; c < children.size(); ++c) {
				Character child = children.get(c);
				if(child != null) {
					JLabel childLabel = new JLabel(child.getName());
					childLabel.setBounds(80, 315 + c*30, 150, 20);
					mainCard.add(childLabel);
					
					JButton addChild = new JButton("Remove");
					addChild.setActionCommand(Integer.toString(child.getID()));
					addChild.setBounds(10, 315 + c*30, 60, 20);
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
							start(person.getID(), true);
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
						person.setName(nmLabel.getText());
						person.setNickName(nicknameLabel.getText());
						person.setBirthday(bdayLabel.getText());
						person.setDeathday(ddayLabel.getText());
					}

					printData(CHARACTER);
					
					start(id, !edit);
					cl.show(mainCards, "Main Card");
				}
			});

			mainCard.add(nameLabel);
			mainCard.add(nnameLabel);
			mainCard.add(nmLabel);
			mainCard.add(nicknameLabel);
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

			JLabel nicknameLabel = new JLabel(person.getNickName());
			width = (int) Math.ceil(nicknameLabel.getPreferredSize().getWidth());
			nicknameLabel.setBounds((WIDTH-width)/2, 45, width, 20);
			
			JLabel genderLabel = new JLabel("Gender: " + person.getGender());
			genderLabel.setBounds(10, 75, 100, 20);
			
			JLabel bdayLabel = new JLabel("Birthday: " + person.getBirthday());
			bdayLabel.setBounds(10, 105, 200, 20);
			
			JLabel ddayLabel = new JLabel("Deathday: " + person.getDeathday());
			ddayLabel.setBounds(10, 135, 200, 20);
			
			JLabel dadLabel = new JLabel("Father:");
			dadLabel.setBounds(10, 165, 50, 20);
			
			if(person.getFather() != null) {
				JLabel dadName = new JLabel(person.getFatherName());
				dadName.setBounds(80, 165, (int) Math.ceil(dadName.getPreferredSize().getWidth()), 20);
				dadName.addMouseListener(new MouseListener() {
		
					@Override
					public void mouseClicked(MouseEvent e) {
						CardLayout cl = (CardLayout) (mainCards.getLayout());
						start(person.getFather().getID(), false);
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
						dadName.setForeground(Color.BLUE);
						dadName.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
						dadName.setText("<html><u>" + person.getFatherName() + "</u></html>");
						
						mainCard.revalidate();
						mainCard.repaint();
					}
		
					@Override
					public void mouseExited(MouseEvent e) {
						dadName.setForeground(Color.BLACK);
						dadName.setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
						dadName.setText(person.getFatherName());
						
						mainCard.revalidate();
						mainCard.repaint();
					}
					
				});

				mainCard.add(dadName);
			}
			
			JLabel momLabel = new JLabel("Mother:");
			momLabel.setBounds(10, 195, 50, 20);
			
			if(person.getMother() != null) {
				JLabel momName = new JLabel(person.getMotherName());
				momName.setBounds(80, 195, (int) Math.ceil(momName.getPreferredSize().getWidth()), 20);
				momName.addMouseListener(new MouseListener() {
		
					@Override
					public void mouseClicked(MouseEvent e) {
						CardLayout cl = (CardLayout) (mainCards.getLayout());
						start(person.getMother().getID(), false);
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
						momName.setForeground(Color.BLUE);
						momName.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
						momName.setText("<html><u>" + person.getMotherName() + "</u></html>");
						
						mainCard.revalidate();
						mainCard.repaint();
					}
		
					@Override
					public void mouseExited(MouseEvent e) {
						momName.setForeground(Color.BLACK);
						momName.setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
						momName.setText(person.getMotherName());
						
						mainCard.revalidate();
						mainCard.repaint();
					}
					
				});
				
				mainCard.add(momName);
			}
			
			JLabel spouseLabel = new JLabel("Spouses:");
			spouseLabel.setBounds(10, 225, 60, 20);
			
			ArrayList<Character> spouses = person.getSpouses();
			ArrayList<Character> children = person.getChildren();
			@SuppressWarnings("unchecked")
			ArrayList<Character> others = (ArrayList<Character>) children.clone();
			int count = 0;
			
			for(int s = 0; s < spouses.size(); ++s) {
				Character spouse = spouses.get(s);
				
				if(spouse != null) {
					count++;
					
					JLabel spouseName = new JLabel(spouse.getName());
					spouseName.setBounds(80 + s*120, 225, (int) Math.ceil(spouseName.getPreferredSize().getWidth()), 20);
					spouseName.addMouseListener(new MouseListener() {
						
						@Override
						public void mouseClicked(MouseEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							start(spouse.getID(), false);
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
							spouseName.setForeground(Color.BLUE);
							spouseName.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
							spouseName.setText("<html><u>" + spouse.getName() + "</u></html>");
							
							mainCard.revalidate();
							mainCard.repaint();
						}
		
						@Override
						public void mouseExited(MouseEvent e) {
							spouseName.setForeground(Color.BLACK);
							spouseName.setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
							spouseName.setText(spouse.getName());
							
							mainCard.revalidate();
							mainCard.repaint();
						}
						
					});
					
					int mult = 0;

					for(int c = 0; c < children.size(); ++c) {
						Character child = children.get(c);
						if(child != null && (child.getFather() == spouse || child.getMother() == spouse)) {
							others.remove(child);
							
							JLabel childLabel = new JLabel(child.getName());
							childLabel.setBounds(80 + s*120, 255 + mult*30, (int) Math.ceil(childLabel.getPreferredSize().getWidth()), 20);
							childLabel.addMouseListener(new MouseListener() {
				
								@Override
								public void mouseClicked(MouseEvent e) {
									CardLayout cl = (CardLayout) (mainCards.getLayout());
									start(child.getID(), false);
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
									childLabel.setForeground(Color.BLUE);
									childLabel.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
									childLabel.setText("<html><u>" + child.getName() + "</u></html>");
									
									mainCard.revalidate();
									mainCard.repaint();
								}
				
								@Override
								public void mouseExited(MouseEvent e) {
									childLabel.setForeground(Color.BLACK);
									childLabel.setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
									childLabel.setText(child.getName());

									mainCard.revalidate();
									mainCard.repaint();
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
					JLabel childLabel = new JLabel(child.getName());
					childLabel.setBounds(80 + count*120, 255 + c*30, (int) Math.ceil(childLabel.getPreferredSize().getWidth()), 20);
					childLabel.addMouseListener(new MouseListener() {
		
						@Override
						public void mouseClicked(MouseEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							start(child.getID(), false);
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
							childLabel.setForeground(Color.BLUE);
							childLabel.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
							childLabel.setText("<html><u>" + child.getName() + "</u></html>");
							
							mainCard.revalidate();
							mainCard.repaint();
						}
		
						@Override
						public void mouseExited(MouseEvent e) {
							childLabel.setForeground(Color.BLACK);
							childLabel.setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
							childLabel.setText(child.getName());

							mainCard.revalidate();
							mainCard.repaint();
						}
						
					});
					
					mainCard.add(childLabel);
				}
			}
				
			JLabel issue = new JLabel("Children:");
			issue.setBounds(10, 255, 100, 20);
			
			JPanel panel = new JPanel(null);
			int level = 0;

			JLabel heldTitles = new JLabel("Titles Held:");
			int w = (int) Math.ceil(heldTitles.getPreferredSize().getWidth());
			heldTitles.setBounds(WIDTH - labelWidth - 120, 75, w, 20);
			mainCard.add(heldTitles);
			
			for(int i = 0; i < person.getTitles().size(); ++i) {
				Title title = person.getTitles().get(i);
				
				JLabel label = new JLabel(title.getTitle());
				w = (int) Math.ceil(label.getPreferredSize().getWidth());
				label.setBounds(50 + (labelWidth - w)/2, 8 + 45*level, w, 20);
				label.addMouseListener(new MouseListener() {
					
					@Override
					public void mouseClicked(MouseEvent e) {
						CardLayout cl = (CardLayout) (mainCards.getLayout());
						fiefPage(title.getFief());
						cl.show(mainCards, "Fief Page Card");
					}
	
					@Override
					public void mousePressed(MouseEvent e) {
						
					}
	
					@Override
					public void mouseReleased(MouseEvent e) {
						
					}
	
					@Override
					public void mouseEntered(MouseEvent e) {
						label.setForeground(Color.BLUE);
						label.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
						label.setText("<html><u>" + title.getTitle() + "</u></html>");

						mainCard.revalidate();
						mainCard.repaint();
					}
	
					@Override
					public void mouseExited(MouseEvent e) {
						label.setForeground(Color.BLACK);
						label.setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
						label.setText(title.getTitle());
						
						mainCard.revalidate();
						mainCard.repaint();
					}
					
				});
				
				JLabel reign = new JLabel("(" + title.getStartDate().getYear() + " - " + title.getEndDate().getYear() + ")");
				w = (int) Math.ceil(reign.getPreferredSize().getWidth());
				reign.setBounds(50 + (labelWidth - w)/2, 23 + 45*level, w, 20);
				
				if(title.getPredecessor() != null) {
					JButton back = new JButton("<");
					//back.setFont(new Font("Helvetica", 16, Font.BOLD));
					back.setBounds(10, 10 + 45*level, 30, 30);
					back.addActionListener(new ActionListener() {

						@Override
						public void actionPerformed(ActionEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							Character p = title.getPredecessor().getRuler();
							start(p.getID(), false);
							cl.show(mainCards, "Main Card");
						}
					});
					panel.add(back);				
				}
				
				if(title.getSuccessor() != null) {
					JButton next = new JButton(">");
					//next.setFont(new Font("Helvetica", 16, Font.BOLD));
					next.setBounds(labelWidth + 60, 10 + 45*level, 30, 30);
					next.addActionListener(new ActionListener() {

						@Override
						public void actionPerformed(ActionEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							Character p = title.getSuccessor().getRuler();
							start(p.getID(), false);
							cl.show(mainCards, "Main Card");
						}
					});
					panel.add(next);
				}
				
				panel.add(label);
				panel.add(reign);
				
				level++;
			}
			
			panel.setPreferredSize(new Dimension(labelWidth + 100, 20 + level*55));
			
			JPanel scrollPanel = new JPanel(new BorderLayout());
			scrollPanel.setBounds(WIDTH - labelWidth - 120, 95, labelWidth + 104, 400);

			JScrollPane scrollPane = new JScrollPane(panel);
			
			scrollPanel.add(scrollPane, BorderLayout.CENTER);
			
			mainCard.add(scrollPanel);
			
			editButton.addActionListener(new ActionListener() {

				@Override
				public void actionPerformed(ActionEvent e) {
					CardLayout cl = (CardLayout) (mainCards.getLayout());
					start(id, !edit);
					cl.show(mainCards, "Main Card");
				}
			});

			mainCard.add(nmLabel);
			mainCard.add(nicknameLabel);
			mainCard.add(genderLabel);
			mainCard.add(spouseLabel);
			mainCard.add(issue);
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
				
				Character child = (Character) r_inv.getTarget();
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
				
				Character spouse = (Character) r_inv.getTarget();
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
				
				Character dad = (Character) r_inv.getTarget();
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
				
				Character mom = (Character) r_inv.getTarget();
				
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
				
				start(person.getID(), false);
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
	public static void chooseCharacter(Relation r, String search) {
		JPanel chooseCharCard = new JPanel(null);
		
		//System.out.println("relation: " + type);
		
		JButton back = new JButton("Back");
		back.setBounds(10, 10, 60, 20);
		back.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				CardLayout cl = (CardLayout) (mainCards.getLayout());
				start(r.getSelf().getID(), true);
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
				addCharacter(new Relation(r.getSelf(), null, r.getType()));
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
				
		getPossibleChars(panel, r, searchField.getText());
		
		searchField.getDocument().addDocumentListener(new DocumentListener() {

			@Override
			public void insertUpdate(DocumentEvent e) {
				//System.out.println("Insert Update: " + searchField.getText());
				
				getPossibleChars(panel, r, searchField.getText());
				chooseCharCard.revalidate();
				chooseCharCard.repaint();
			}

			@Override
			public void removeUpdate(DocumentEvent e) {
				//System.out.println("Remove Update");	
				
				getPossibleChars(panel, r, searchField.getText());
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

		JScrollPane scrollPane = new JScrollPane(panel);
		//scrollPane.setPreferredSize(new Dimension(250, 400));
		
		scrollPanel.add(scrollPane, BorderLayout.CENTER);
		
		chooseCharCard.add(scrollPanel);
		
		mainCards.add(chooseCharCard, CCHAR);
	}
	public static JPanel getPossibleChars(JPanel panel, Relation r, String search) {
		panel.removeAll();

		//System.out.println("relation: " + type);
		
		int level = 0;
		
		for(int i = 0; i < charList.size(); ++i) {
			Character c = charList.get(i);
			
			boolean display = false;
			
			if(r.getType() == Relation.FATHER && c.getGenderInt() == Character.MALE) {
				display = true;
			}
			else if(r.getType() == Relation.MOTHER && c.getGenderInt() == Character.FEMALE) {
				display = true;
			}
			else if(r.getType() == Relation.CHILD && !((Character) r.getSelf()).isChild(i))
				display = true;
			else if(r.getType() == Relation.SPOUSE && !((Character) r.getSelf()).isSpouse(i))
				display = true;
			else if(r.getType() == Relation.PREDECESSOR) {
				
			}
			
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
							
							Relation rel = new Relation(r.getSelf(), choice, r.getType());
							
							//System.out.println(r);
							((Character) r.getSelf()).setRelation(rel);
							choice.setRelation(rel.getInverse());
							
							start(r.getSelf().getID(), true);
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
		panel.setPreferredSize(new Dimension(320, 20 + level*55));
		
		return panel;
	}
	public static void chooseTitle(Relation r, Title title) {
		JPanel chooseTitleCard = new JPanel(null);
		
		//System.out.println("relation: " + type);
		
		JButton back = new JButton("Back");
		back.setBounds(10, 10, 60, 20);
		back.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				CardLayout cl = (CardLayout) (mainCards.getLayout());
				start(r.getSelf().getID(), true);
				cl.show(mainCards, "Main Card");
			}
		});
		chooseTitleCard.add(back);
		
		JButton newChar = new JButton("New");
		newChar.setBounds(10, 40, 60, 20);
		newChar.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				CardLayout cl = (CardLayout) (mainCards.getLayout());
				//addTitle(new Relation(self.getID(), charList.size(), type));
				cl.show(mainCards, "New Title Card");
			}
		});
		chooseTitleCard.add(newChar);
		
		JLabel searchLabel = new JLabel("Search:");
		searchLabel.setBounds(145, 20, 55, 20);
		chooseTitleCard.add(searchLabel);

		JTextField searchField = new JTextField();
		searchField.setBounds(200, 20, 200, 20);
		
		JPanel panel = new JPanel(null);
				
		getPossibleTitles(panel, r, searchField.getText(), title);
		
		searchField.getDocument().addDocumentListener(new DocumentListener() {

			@Override
			public void insertUpdate(DocumentEvent e) {
				//System.out.println("Insert Update: " + searchField.getText());
				
				getPossibleTitles(panel, r, searchField.getText(), title);
				chooseTitleCard.revalidate();
				chooseTitleCard.repaint();
			}

			@Override
			public void removeUpdate(DocumentEvent e) {
				//System.out.println("Remove Update");	
				
				getPossibleTitles(panel, r, searchField.getText(), title);
				chooseTitleCard.revalidate();
				chooseTitleCard.repaint();
			}

			@Override
			public void changedUpdate(DocumentEvent e) {
				
			}
		});
	
		chooseTitleCard.add(searchField);
		
		JPanel scrollPanel = new JPanel(new BorderLayout());
		scrollPanel.setBounds(100, 50, 350, 400);

		JScrollPane scrollPane = new JScrollPane(panel);
		//scrollPane.setPreferredSize(new Dimension(250, 400));
		
		scrollPanel.add(scrollPane, BorderLayout.CENTER);
		
		chooseTitleCard.add(scrollPanel);
		
		mainCards.add(chooseTitleCard, CTCARD);
	}
	public static JPanel getPossibleTitles(JPanel panel, Relation r, String search, Title title) {
		panel.removeAll();

		//System.out.println("relation: " + type);
		
		int level = 0;
		
		for(int i = 0; i < fiefList.size(); ++i) {
			Fief f = fiefList.get(i);
			
			boolean display = true;
			
			ArrayList<Title> titles = f.getTitles();
			
			for(int t = 0; t < titles.size(); ++i)
				if(titles.get(t).contains(title)) {
					display = false;
					break;
				}
				
			if(display) {
				if(search == null || f.getName().contains(search)) {
					//System.out.println("Char: " + c.getName() + ", Search: " + search);
					JLabel nameLabel = new JLabel(f.getFullName());
					nameLabel.setBounds(10, 10+level*55, 200, 20);
					
					/*
					JLabel born = new JLabel("Born: " + c.getBirthday());
					//lifeLabel.setText("( " + c.getBirthday() + " - " + c.getDeathday() + " )");
					born.setBounds(30, 25+level*55, 170, 20);
					
					JLabel died = new JLabel("Died: " + c.getDeathday());
					//lifeLabel.setText("( " + c.getBirthday() + " - " + c.getDeathday() + " )");
					died.setBounds(30, 40+level*55, 170, 20);
					*/
					
					JButton choose = new JButton("Choose");
					choose.setBounds(250, 25 + level*55, 60, 20);
					choose.setActionCommand(Integer.toString(f.getID()));
					choose.addActionListener(new ActionListener() {
		
						@Override
						public void actionPerformed(ActionEvent e) {
							CardLayout cl = (CardLayout) (mainCards.getLayout());
							
							Character choice = charList.get(Integer.parseInt(e.getActionCommand()));
							
							Relation rel = new Relation(r.getSelf(), choice, r.getType());
							
							//System.out.println(r);
							((Character) r.getSelf()).setRelation(rel);
							choice.setRelation(rel.getInverse());
							
							start(r.getSelf().getID(), true);
							cl.show(mainCards, "Main Card");
						}
					});
					
					level++;

					//panel.add(died);
					//panel.add(born);
					panel.add(nameLabel);
					panel.add(choose);
				}
			}
		}
		panel.setPreferredSize(new Dimension(320, 20 + level*55));
		
		return panel;
	}
	public static void fiefPage(Fief f) {
		JPanel fiefPageCard = new JPanel(null);
		
		JLabel nmLabel = new JLabel(f.getName());
		nmLabel.setFont(new Font("Helvetica", Font.BOLD, 24));
		int width = (int) Math.ceil(nmLabel.getPreferredSize().getWidth());
		nmLabel.setBounds((WIDTH-width)/2, 10, width, 50);
		fiefPageCard.add(nmLabel);
		
		
		
		mainCards.add(fiefPageCard, FPCARD);
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
					
					line = line + person.getID() + ";" + person.getName() + ";" + person.getNickName() + ";"
					+ person.getGenderInt() + ";" + person.getBirthday() + ";" + person.getDeathday() + ";";
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
			 * Fief Name (String)
			 * Fief Type (int)
			 */
		}
		else if(type == TITLE) {
			/**
			 * Title ID (int)
			 * Fief ID (int)
			 * Ruler ID (int)
			 * Ruler Start Date (String)
			 * Ruler End Date (String)
			 * Predecessor Title ID (int)
			 * Successor Title ID (int)
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
					person.setNickName(values[2]);
					person.setGender(Integer.parseInt(values[3]));
					
					person.setBirthday(values[4]);
					person.setDeathday(values[5]);
					
					if(person.getID() != Integer.parseInt(values[0]))
						System.out.println("Error: Mismatched IDs. ID Read: " + values[0] + ", ID Set: " + person.getID());
					else {
						person.addRelation(new Relation(person, new Entity(Integer.parseInt(values[6])), Relation.FATHER));
						person.addRelation(new Relation(person, new Entity(Integer.parseInt(values[7])), Relation.MOTHER));
						String[] spouse = values[8].split(",");
						for(int i = 0; i < spouse.length; ++i)
							person.addRelation(new Relation(person, new Entity(Integer.parseInt(spouse[i])), Relation.SPOUSE));
						String[] issue = values[9].split(",");
						for(int i = 0; i < issue.length; ++i)
							person.addRelation(new Relation(person, new Entity(Integer.parseInt(issue[i])), Relation.CHILD));
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
			titleList.clear();
			try {
				BufferedReader reader = new BufferedReader(new FileReader(new File("src/fiefs.txt")));
				String line;
				while(!((line = reader.readLine()) == null)) {
					String[] values = line.split(";");
					
					fiefList.add(new Fief(Integer.parseInt(values[0]), values[1], Integer.parseInt(values[2])));
				}
				
				reader.close();
			} catch (IOException e) {
				System.out.println(e.getMessage());
			}
		}
		else if(type == TITLE) {
			titleList.clear();
			try {
				BufferedReader reader = new BufferedReader(new FileReader(new File("src/titles.txt")));
				String line;
				while(!((line = reader.readLine()) == null)) {
					String[] values = line.split(";");
					
					Character ruler = charList.get(Integer.parseInt(values[2]));
					Fief fief = fiefList.get(Integer.parseInt(values[1]));
					
					Title title = new Title(getDate(values[3], 0), fief, ruler, getDate(values[4], 1));
					
					if(title.getID() != Integer.parseInt(values[0]))
						System.out.println("Error: Mismatched IDs. ID Read: " + values[0] + ", ID Set: " + title.getID());
					else {
						title.addRelation(new Relation(title, new Entity(Integer.parseInt(values[5])), Relation.PREDECESSOR));
						title.addRelation(new Relation(title, new Entity(Integer.parseInt(values[6])), Relation.SUCCESSOR));
					}
					
					titleList.add(title);
				}
				setTitles();
				reader.close();
			} catch (IOException e) {
				System.out.println(e.getMessage());
			}
		}
		else
			System.out.println("Error: Invalid Type");
	}
	public static LocalDate getDate(String date, int relation) {
		int START = 0;
		int END = 1;
		String[] parts = date.split(" ");
		if(parts.length == 3)
			return LocalDate.of(Integer.parseInt(parts[2]), getMonth(parts[1]), Integer.parseInt(parts[0]));
		else if(parts.length == 1) {
			if(relation == START)
				return LocalDate.of(Integer.parseInt(parts[0]), 6, 15);
			else if(relation == END)
				return LocalDate.of(Integer.parseInt(parts[0]), 6, 14);
			else
				return null;
		}
		else if(parts[0].contains(".")) {
			if(relation == START)
				return LocalDate.of(Integer.parseInt(parts[1]), 6, 15);
			else if(relation == END)
				return LocalDate.of(Integer.parseInt(parts[1]), 6, 14);
			else
				return null;
		}
		else {
			if(relation == START)
				return LocalDate.of(Integer.parseInt(parts[1]), getMonth(parts[0]), 15);
			else if(relation == END)
				return LocalDate.of(Integer.parseInt(parts[1]), getMonth(parts[0]), 14);
			else
				return null;
		}
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
	public static void setTitles() {
		for(int i = 0; i < titleList.size(); ++i) {
			Title title = titleList.get(i);
			ArrayList<Relation> relations = title.getRelations();
			for(int j = 0; j < relations.size(); ++j) {
				Relation r = relations.get(j);
				Title target = r.getTarget();
				
				if(r.getType() == Relation.PREDECESSOR)
					title.setPredecessor(target);
					//System.out.println(target.getID() + " not able to be predecessor of " + title.getID());
				else if(r.getType() == Relation.SUCCESSOR)
					title.setSuccessor(target);
					//System.out.println(target.getID() + " not able to be successor of " + title.getID());
				else
					System.out.println("Error: Invalid Relation Type");
			}
		}
	}
	public static void setCharacters() {
		for(int i = 0; i < charList.size(); ++i) {
			Character person = charList.get(i);
			ArrayList<Relation> relations = person.getRelations();
			for(int j = 0; j < relations.size(); ++j)
				person.setRelation(relations.get(j));
		}
	}
}