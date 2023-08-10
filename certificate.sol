// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CertificateRegistry {
    enum Status { Issued, Revoked, Expired }

    struct Certificate {
        bytes32 id; // Unique ID for the certificate (hashed value)
        string name;
        string issuer;
        address issuerAddress;
        uint256 issueDate;
        Status status; // Status of the certificate
    }

    Certificate[] public certificates;



    // Event to notify when a new certificate is issued
    event CertificateIssued(bytes32 indexed id,string name, string issuer, address issuerAddress, uint256 issueDate, Status status);

    function issueCertificate(
        string memory _name,
        string memory _issuer,
        uint256 _issueDate
    ) public {
        // Perform any necessary validations or access controls here

        // Generate a unique ID using a cryptographic hash function
        bytes32 uniqueId = keccak256(abi.encodePacked(msg.sender, _name, _issuer, _issueDate));

        // Add the new certificate to the registry  with the hashed ID and status "Issued"
        certificates.push(Certificate(uniqueId,_name, _issuer,msg.sender, _issueDate, Status.Issued));

       // Emit an event to notify that a new certificate has been issued
        emit CertificateIssued(uniqueId, _name, _issuer, msg.sender, _issueDate, Status.Issued);
    }


    function getCertificate(uint256 index) public view returns (bytes32,string memory, string memory,address, uint256, Status) {
        require(index < certificates.length, "Invalid certificate index");

        Certificate memory cert = certificates[index];
        return (cert.id, cert.name, cert.issuer, cert.issuerAddress, cert.issueDate, cert.status);
    }

    // Function to revoke a certificate
    function revokeCertificate(uint256 index) public {
        require(index < certificates.length, "Invalid certificate index");

        Certificate storage cert = certificates[index];
        
        // Only the issuer (msg.sender) can revoke the certificate
        require(cert.issuerAddress == msg.sender, "Only the issuer can revoke the certificate");

        // Perform any necessary validations or access controls here

        cert.status = Status.Revoked;
    }

    // Function to expire a certificate
    function expireCertificate(uint256 index) public {
        require(index < certificates.length, "Invalid certificate index");

        Certificate storage cert = certificates[index];
        
        // Only the issuer (msg.sender) can expire the certificate
        require(cert.issuerAddress == msg.sender, "Only the issuer can expire the certificate");

        // Perform any necessary validations or access controls here

        cert.status = Status.Expired;
    }
}