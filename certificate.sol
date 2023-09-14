// SPDX-License-Identifier: MIT
pragma solidity ^0.8.2;

contract CertificateRegistry {

    struct Certificate {
        bytes32 id; // Unique ID for the certificate (hashed value)
        string name;
        string issuer;
        address issuerAddress;
        uint256 issueDate;
    }

    Certificate[] public certificates;

    // Event to notify when a new certificate is issued
    event CertificateIssued(bytes32 indexed id, string name, string issuer, address issuerAddress, uint256 issueDate);

    function issueCertificate(
        string memory _name,
        string memory _issuer,
        uint256 _issueDate
    ) public returns (bytes32, string memory, string memory, address) {
        // Generate a unique ID using a cryptographic hash function
        bytes32 uniqueId = keccak256(abi.encodePacked(msg.sender, _name, _issuer, _issueDate));

        // Create a new Certificate struct
        Certificate memory newCertificate = Certificate(uniqueId, _name, _issuer, msg.sender, _issueDate);

        // Add the new certificate to the registry
        certificates.push(newCertificate);

        // Emit an event to notify that a new certificate has been issued
        emit CertificateIssued(uniqueId, _name, _issuer, msg.sender, _issueDate);

        // Return the certificate details
        return (uniqueId, _name, _issuer, msg.sender);
    }

    function getCertificate(uint256 index) public view returns (bytes32, string memory, string memory, address, uint256) {
        require(index < certificates.length, "Invalid certificate index");

        Certificate memory cert = certificates[index];
        return (cert.id, cert.name, cert.issuer, cert.issuerAddress, cert.issueDate);
    }

     // Function to verify the status of a certificate by its unique ID
    function verifyCertificate(bytes32 certificateId) public view returns (bool) {
        for (uint256 i = 0; i < certificates.length; i++) {
            if (certificates[i].id == certificateId) {
                return true; // Certificate with the provided ID exists
            }
        }
        return false; // Certificate with the provided ID does not exist
    }
}
