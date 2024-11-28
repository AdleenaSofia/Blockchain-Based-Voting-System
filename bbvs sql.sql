-- create database
CREATE DATABASE bbvs1;
USE bbvs1;

-- creating student table
CREATE TABLE Student(
	StudentID varchar(45) PRIMARY KEY, 
    Name varchar(45),
    Email varchar(45),
    Course varchar(45),
    Semester varchar(45)
);

-- creating Admin table
CREATE TABLE Admin(
	ID int PRIMARY KEY AUTO_INCREMENT,
    Username varchar(45),
    Password varchar(45)
);

-- insert an Admin to Admin Table
INSERT INTO Admin (Username,Password) VALUES ('admin','admin123');

-- creating Election table
CREATE TABLE Election (
	ElectionID INT PRIMARY KEY AUTO_INCREMENT,
    ElectionName varchar(100),
    ElectionDate DATE,
    status VARCHAR(20)
);

-- creating Candidate table
CREATE TABLE Candidate (
    CandidateID INT PRIMARY KEY AUTO_INCREMENT,
    StudentID VARCHAR(45),
    ElectionID INT,
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
    FOREIGN KEY (ElectionID) REFERENCES Election(ElectionID)
);

-- creating Ballot table
CREATE TABLE Ballot(
	VoteID INT PRIMARY KEY AUTO_INCREMENT,
    VoterID varchar(45),
    ElectionID INT,
    CandidateID INT,
    FOREIGN KEY (VoterID) REFERENCES Student(StudentID),
    FOREIGN KEY (ElectionID) REFERENCES Election(ElectionID),
    FOREIGN KEY (CandidateID) REFERENCES Candidate(CandidateID)
);



